"""Controlled study: one-step quantile ranking versus lead-time newsvendor cost.

Synthetic stationary Gaussian AR(1). Runs only a specified protocol, not model search.
No external datasets, agents, or publication claims.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import subprocess
import platform
import random
import statistics
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from statistics import NormalDist

NORMAL = NormalDist()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()

def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def lag_variance(length, rho):
    """Variance of sum of length stationary AR(1) standard-normal marginals."""
    return length + 2 * sum((length - lag) * rho**lag for lag in range(1, length))

def pinball(y, q, alpha):
    return (alpha if y >= q else alpha - 1) * (y - q)

def newsvendor_cost(y, q, alpha):
    return (1 - alpha) * max(q - y, 0) + alpha * max(y - q, 0)

def gaussian_expected_cost(mean, sd, q, alpha):
    """Analytic expected newsvendor loss for D ~ Normal(mean, sd)."""
    z = (q - mean) / sd
    pdf = math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
    cdf = NORMAL.cdf(z)
    excess = (q - mean) * cdf + sd * pdf
    shortage = sd * pdf - (q - mean) * (1 - cdf)
    return (1 - alpha) * excess + alpha * shortage

def evaluate_cell(config, length, rho, alpha, padding, seed):
    mu, sigma = config['mean'], config['sigma']
    n = config['trials_per_seed']
    z = NORMAL.inv_cdf(alpha)
    qa = length * mu + z * sigma * math.sqrt(length)
    qb = length * mu + z * sigma * math.sqrt(length) * (1 + padding)
    qo = length * mu + z * sigma * math.sqrt(lag_variance(length, rho))
    qda, qdb = mu + z * sigma, mu + z * sigma * (1 + padding)
    rng = random.Random(f"{config['generator_version']}|{seed}|{length}|{rho}|{alpha}|{padding}")
    cost_a = cost_b = cost_o = daily_a = daily_b = 0.0
    root = math.sqrt(1 - rho * rho)
    for _ in range(n):
        state = rng.gauss(0, 1)
        first = mu + sigma * state
        total = first
        for _ in range(length - 1):
            state = rho * state + root * rng.gauss(0, 1)
            total += mu + sigma * state
        daily_a += pinball(first, qda, alpha)
        daily_b += pinball(first, qdb, alpha)
        cost_a += newsvendor_cost(total, qa, alpha)
        cost_b += newsvendor_cost(total, qb, alpha)
        cost_o += newsvendor_cost(total, qo, alpha)
    return {
        'seed': seed,
        'daily_pinball_A': daily_a/n,
        'daily_pinball_B': daily_b/n,
        'cost_A': cost_a/n,
        'cost_B': cost_b/n,
        'cost_oracle': cost_o/n,
        'B_minus_A': (cost_b - cost_a)/n,
    }

def summarize(rows):
    vals = [r['B_minus_A'] for r in rows]
    avg = statistics.fmean(vals)
    # Student-t 95% approximation for 3 or 8 independent seed blocks.
    tcrit = {3:4.303, 8:2.365}.get(len(vals))
    stderr = statistics.stdev(vals)/math.sqrt(len(vals)) if len(vals)>1 else None
    return {
        'n_seed_blocks':len(vals), 'trials_per_block':rows[0].get('_trials'),
        'difference_B_minus_A':avg,
        'ci_95': [avg-tcrit*stderr,avg+tcrit*stderr] if tcrit and stderr is not None else None,
        'daily_pinball_B_minus_A':statistics.fmean(r['daily_pinball_B']-r['daily_pinball_A'] for r in rows),
        'cost_A':statistics.fmean(r['cost_A'] for r in rows),
        'cost_B':statistics.fmean(r['cost_B'] for r in rows),
        'oracle_cost':statistics.fmean(r['cost_oracle'] for r in rows),
    }

def run_protocol(config):
    if config['phase'] not in {'exploratory', 'confirmatory'}:
        raise ValueError('Unsupported research phase')
    if not config.get('seeds') or len(set(config['seeds'])) != len(config['seeds']):
        raise ValueError('Independent seeds must be unique')
    if not config.get('lead_times') or not config.get('rhos') or not config.get('paddings') or not config.get('alphas'):
        raise ValueError('Empty experimental grid')
    if config['phase']=='confirmatory' and config.get('frozen') is not True:
        raise ValueError('Confirmatory protocol must be frozen')
    if not (config['generator_version']=='gaussian-ar1-v1' and 0 < config['sigma'] and config['mean'] > 6*config['sigma']):
        raise ValueError('Protocol generator or nonnegative-demand bound unsupported')
    if not 1<=config['trials_per_seed']<=1000000:
        raise ValueError('Invalid trial count')
    output=[]
    for alpha in config['alphas']:
        if not 0 < alpha < 1:
            raise ValueError('alpha outside (0,1)')
        for length in config['lead_times']:
            if type(length) is not int or length < 1:
                raise ValueError('Invalid lead-time length')
            for rho in config['rhos']:
                if not 0 <= rho < 1:
                    raise ValueError('rho outside [0,1)')
                for padding in config['paddings']:
                    if padding < 0:
                        raise ValueError('padding cannot be negative')
                    blocks=[evaluate_cell(config,length,rho,alpha,padding,seed) for seed in config['seeds']]
                    for b in blocks: b['_trials']=config['trials_per_seed']
                    item={'alpha':alpha,'lead_time':length,'rho':rho,'padding':padding, **summarize(blocks)}
                    z=NORMAL.inv_cdf(alpha)
                    sd=config['sigma']*math.sqrt(lag_variance(length,rho))
                    item['analytic_B_minus_A'] = (
                        gaussian_expected_cost(length*config['mean'],sd,length*config['mean']+z*config['sigma']*math.sqrt(length)*(1+padding),alpha)
                        - gaussian_expected_cost(length*config['mean'],sd,length*config['mean']+z*config['sigma']*math.sqrt(length),alpha)
                    )
                    item['blocks']=blocks
                    output.append(item)
    return {'question_id':config['question_id'],'phase':config['phase'], 'protocol_sha256':sha(config),
            'dataset_fingerprint':sha({'generator':config['generator_version'],'mean':config['mean'],'sigma':config['sigma']}),
            'statistical_unit':'independent Monte Carlo block / seed',
            'primary_difference':'B_minus_A; negative indicates decision rank reversal',
            'frozen':config['frozen'], 'cells':output}

def current_git_commit():
    try:
        return subprocess.check_output(['git','rev-parse','HEAD'],
                                       stderr=subprocess.DEVNULL,timeout=3).decode().strip()
    except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired):
        return None


def source_digest():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def write_artifacts(config_path, output):
    """Create immutable-by-interface run package containing protocol and results."""
    config_path=Path(config_path)
    config=json.loads(config_path.read_text(encoding='utf-8'))
    began=time.perf_counter()
    result=run_protocol(config)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    config_bytes=canonical(config)
    payload=canonical(result)
    manifest={
        'phase':config['phase'],'protocol_sha256':sha(config),
        'result_sha256':hashlib.sha256(payload).hexdigest(),
        'dataset_fingerprint':result['dataset_fingerprint'],
        'config_source':str(config_path),'seeds':config['seeds'],
        'n_trials_per_seed':config['trials_per_seed'],
        'baselines':['iid_aggregate_quantile_A','inflated_iid_quantile_B','true_AR1_oracle'],
        'metric':'mean asymmetric newsvendor cost; daily pinball',
        'compute_seconds':time.perf_counter()-began,
        'environment':{'python':sys.version.split()[0],'platform':platform.platform()},
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'code_sha256':source_digest(),'git_commit':current_git_commit(),
        'scientific_status':'NOT_PUBLICATION_READY',
        'notes':'Artifact integrity is not independent preregistration or scientific validity',
    }
    from research_lab.engine import write_new
    write_new(output/'config.json',config_bytes)
    write_new(output/'results.json',payload)
    write_new(output/'manifest.json',canonical(manifest))
    return result,manifest


def verify_artifacts(output, *, config_path=None, replay=False):
    """Audit SHA256, exact source protocol, and optionally replay the simulation.

    Coordinated malicious edits to manifest and data cannot be ruled out by hashes
    alone. Protect signed commits and externally archived CI evidence.
    """
    output=Path(output)
    manifest=json.loads((output/'manifest.json').read_bytes())
    cfg_bytes=(output/'config.json').read_bytes()
    result_bytes=(output/'results.json').read_bytes()
    config=json.loads(cfg_bytes)
    result=json.loads(result_bytes)
    if canonical(config)!=cfg_bytes:
        raise ValueError('Config bytes not canonical')
    if hashlib.sha256(cfg_bytes).hexdigest()!=manifest['protocol_sha256']:
        raise ValueError('Protocol fingerprint mismatch')
    if hashlib.sha256(result_bytes).hexdigest()!=manifest['result_sha256']:
        raise ValueError('Result hash mismatch')
    if result['protocol_sha256']!=manifest['protocol_sha256'] or result['phase']!=manifest['phase']:
        raise ValueError('Result/protocol phase or hash mismatch')
    expected_data=sha({'generator':config['generator_version'],'mean':config['mean'],'sigma':config['sigma']})
    if result['dataset_fingerprint']!=expected_data or manifest['dataset_fingerprint']!=expected_data:
        raise ValueError('Data generator fingerprint mismatch')
    if source_digest()!=manifest['code_sha256']:
        raise ValueError('Experiment implementation differs from run')
    if config_path is not None and canonical(json.loads(Path(config_path).read_text()))!=cfg_bytes:
        raise ValueError('Saved config differs from declared protocol')
    if replay and canonical(run_protocol(config))!=result_bytes:
        raise ValueError('Replay does not match archived results')
    return {'status':'PASS','phase':manifest['phase'],'cells':len(result['cells']),
            'protocol_sha256':manifest['protocol_sha256'],
            'replay_performed':replay,'run_commit':manifest['git_commit']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--verify',action='store_true',help='Audit saved evidence and replay simulation')
    args=p.parse_args()
    if args.verify:
        print(json.dumps(verify_artifacts(args.output,config_path=args.config,replay=True),sort_keys=True))
        return
    result,manifest=write_artifacts(args.config,args.output)
    rows=result['cells']
    primary=[x for x in rows if x['alpha']==.9 and x['lead_time']==7 and x['rho']==.6 and x['padding']==.45]
    print(f"phase={result['phase']} protocol_sha={result['protocol_sha256']} cells={len(rows)}")
    print(f"primary_cell={json.dumps({k:v for k,v in primary[0].items() if k!='blocks'},sort_keys=True)}" if primary else 'No primary cell')
    print(f"mean_absolute_simulation_vs_analytic_gap={statistics.fmean(abs(r['difference_B_minus_A']-r['analytic_B_minus_A']) for r in rows):.6f}")
    print(f"artifact_manifest={args.output}/manifest.json")


if __name__=='__main__':main()
