"""Controlled study: one-step quantile ranking versus lead-time newsvendor cost.

Synthetic stationary Gaussian AR(1). Runs only a specified protocol, not model search.
No external datasets, agents, or publication claims.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import platform
import random
import statistics
import sys
import time
from pathlib import Path
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
    if config['phase']=='confirmatory' and config.get('frozen') is not True:
        raise ValueError('Confirmatory protocol must be frozen')
    if not (config['generator_version']=='gaussian-ar1-v1' and config['mean']>6*config['sigma']):
        raise ValueError('Protocol generator or nonnegative-demand bound unsupported')
    if not 1<=config['trials_per_seed']<=1000000:
        raise ValueError('Invalid trial count')
    output=[]
    for alpha in config['alphas']:
        assert 0<alpha<1
        for length in config['lead_times']:
            assert length>=1
            for rho in config['rhos']:
                assert 0<=rho<1
                for padding in config['paddings']:
                    assert padding>=0
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

def write_artifacts(config_path, output):
    config_path=Path(config_path)
    config=json.loads(config_path.read_text())
    began=time.perf_counter()
    result=run_protocol(config)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    payload=canonical(result)
    (output/'results.json').write_bytes(payload)
    manifest={'phase':config['phase'],'protocol_sha256':sha(config),'result_sha256':hashlib.sha256(payload).hexdigest(),
              'config_source':str(config_path),'seeds':config['seeds'],'n_trials_per_seed':config['trials_per_seed'],
              'baselines':['iid_aggregate_quantile_A','inflated_iid_quantile_B','true_AR1_oracle'],
              'metric':'mean asymmetric newsvendor cost; daily pinball',
              'compute_seconds':time.perf_counter()-began,
              'environment':{'python':sys.version.split()[0],'platform':platform.platform()},
              'scientific_status':'NOT_PUBLICATION_READY'}
    (output/'manifest.json').write_bytes(canonical(manifest))
    return result,manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    result,manifest=write_artifacts(args.config,args.output)
    rows=result['cells']
    primary=[x for x in rows if x['alpha']==.9 and x['lead_time']==7 and x['rho']==.6 and x['padding']==.45]
    print(f"phase={result['phase']} protocol_sha={result['protocol_sha256']} cells={len(rows)}")
    print(f"primary_cell={json.dumps({k:v for k,v in primary[0].items() if k!='blocks'},sort_keys=True)}" if primary else 'No primary cell')
    print(f"mean_absolute_simulation_vs_analytic_gap={statistics.fmean(abs(r['difference_B_minus_A']-r['analytic_B_minus_A']) for r in rows):.6f}")
    print(f"artifact_manifest={args.output}/manifest.json")

if __name__=='__main__':main()
