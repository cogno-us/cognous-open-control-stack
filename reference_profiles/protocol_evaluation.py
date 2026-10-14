"""Preregistered paired-outcome scoring utilities; no model effectiveness claim."""
import random
from .assurance_runtime import exact, require, names, integer, label, digest


def preregister(*, cases, model, tools_digest, budget, seed, false_positive_cost, false_negative_cost):
    names(cases);label(model);label(tools_digest);integer(budget,1);integer(seed)
    integer(false_positive_cost);integer(false_negative_cost)
    rng=random.Random(seed);allocation=[]
    for case in sorted(cases):
        conditions=['on','off'];rng.shuffle(conditions)
        offset=len(allocation)
        allocation.extend({'id':f'run-{offset+j}','case':case,'condition':condition} for j,condition in enumerate(conditions))
    plan=dict(cases=sorted(cases),model=model,tools_digest=tools_digest,budget=budget,seed=seed,false_positive_cost=false_positive_cost,false_negative_cost=false_negative_cost,allocation=allocation,primary_metric='discriminating_action_change',blinding_alpha=0.05)
    return {'plan':plan,'commitment':digest(plan),'measured_effectiveness':False}


def blinded_outcomes(registration, outcomes):
    """Only outcome fields go to graders. Allocation must be held separately."""
    plan=registration['plan'];require(digest(plan)==registration['commitment'],'PREREGISTRATION_CHANGED')
    require(type(outcomes) is list and len(outcomes)==len(plan['allocation']),'INCOMPLETE_PAIRS')
    expected={x['id']:x['case'] for x in plan['allocation']};seen=set();result=[]
    for o in outcomes:
        exact(o,'id case observations before_action action confidence_ppm truth relevant held_out')
        require(o['id'] not in seen and expected.get(o['id'])==o['case'],'RUN_BINDING');seen.add(o['id'])
        for f in ('before_action','action','truth','relevant','held_out'):require(type(o[f]) is bool,'INVALID_OUTCOME')
        require(integer(o['confidence_ppm'])<=1000000,'INVALID_CONFIDENCE')
        require(type(o['observations']) is list and all(type(x) is str for x in o['observations']),'INVALID_OBSERVATIONS')
        result.append(dict(o))
    return result


def lock_scores(registration, outcomes):
    rows=blinded_outcomes(registration,outcomes);p=registration['plan'];scores=[]
    for row in rows:
        fp=row['action'] and not row['truth'];fn=not row['action'] and row['truth']
        scores.append({'id':row['id'],'action_changed':row['action']!=row['before_action'],'relevant':row['relevant'],'correct':row['action']==row['truth'],'error_cost':int(fp)*p['false_positive_cost']+int(fn)*p['false_negative_cost'],'brier':(row['confidence_ppm']/1000000-int(row['truth']))**2,'held_out':row['held_out']})
    body={'registration':registration['commitment'],'outcomes_digest':digest(rows),'scores':scores}
    return dict(body,commitment=digest(body))


def unblind(registration, locked, guesses):
    body={k:v for k,v in locked.items() if k!='commitment'}
    require(digest(body)==locked['commitment'] and locked['registration']==registration['commitment'],'SCORES_CHANGED')
    require(digest(registration['plan'])==registration['commitment'],'PREREGISTRATION_CHANGED')
    allocation={x['id']:x['condition'] for x in registration['plan']['allocation']}
    require(type(guesses) is dict and set(guesses)==set(allocation) and all(v in ('on','off') for v in guesses.values()),'BLINDING_GUESSES_REQUIRED')
    correct=sum(guesses[k]==v for k,v in allocation.items());n=len(allocation)
    # Paired allocations are dependent: exact permutation over independent pair flips.
    pairs=[registration['plan']['allocation'][i:i+2] for i in range(0,n,2)]
    distribution={0:1}
    for pair in pairs:
        hits=sum(guesses[x['id']]==x['condition'] for x in pair);next_distribution={}
        for score,count in distribution.items():
            for addition in (hits,2-hits):next_distribution[score+addition]=next_distribution.get(score+addition,0)+count
        distribution=next_distribution
    pvalue=sum(count for score,count in distribution.items() if score>=correct)/(2**len(pairs))
    groups={}
    for condition in ('on','off'):
        selected=[s for s in locked['scores'] if allocation[s['id']]==condition]
        relevant=[s for s in selected if s['relevant']];irrelevant=[s for s in selected if not s['relevant']]
        held=[s for s in selected if s['held_out']]
        groups[condition]={'n':len(selected),'discriminating_action_change':sum(s['action_changed'] for s in relevant)/len(relevant) if relevant else None,'nondiscriminating_stability':sum(not s['action_changed'] for s in irrelevant)/len(irrelevant) if irrelevant else None,'error_cost':sum(s['error_cost'] for s in selected),'brier':sum(s['brier'] for s in selected)/len(selected),'held_out_accuracy':sum(s['correct'] for s in held)/len(held) if held else None}
    return {'groups':groups,'blinding_guess_accuracy':correct/n,'blinding_pvalue':pvalue,'blinding_failed':pvalue<registration['plan']['blinding_alpha'],'measured_effectiveness':False,'limitation':'Scoring machinery only; curated ground truth, independent graders and real randomized model trials required.'}
