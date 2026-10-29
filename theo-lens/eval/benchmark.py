#!/usr/bin/env python3
"""Prepare a blinded 10-topic, 3-arm comparison; optional explicit API run."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent / 'skills' / 'theo-lens' / 'SKILL.md'
SYSTEM = ('你是中文讲解助手。请回答用户的问题。所有组均没有网页或外部工具，'
          '不要声称已联网核实；如缺少实时事实请明确说明。')
GENERIC = '请先说明概念或问题，再举例解释机制，指出重要边界，用清晰简洁的语言回答。\n\n'
ARMS = ('plain', 'structured', 'theo_lens')


def build_requests(cases, skill_text, seed):
    requests = []
    for case in cases:
        for arm in ARMS:
            question = case['prompt']
            if arm == 'plain':
                user = question
            elif arm == 'structured':
                user = GENERIC + question
            else:
                user = '请遵循以下技能说明回答，前提是本次没有网页或外部工具：\n\n' + skill_text + '\n\n用户问题：' + question
            code = hashlib.sha256(f'{seed}|{case["id"]}|{arm}'.encode()).hexdigest()[:16]
            requests.append({'id': code, 'case_id': case['id'], 'question': question,
                             'arm': arm, 'system': SYSTEM, 'user': user})
    random.Random(seed).shuffle(requests)
    return requests


def call_api(url, model, api_key, req, timeout):
    body = {'model': model, 'messages': [{'role': 'system', 'content': req['system']},
                                        {'role': 'user', 'content': req['user']}],
            'temperature': 0}
    request = urllib.request.Request(url, data=json.dumps(body, ensure_ascii=False).encode(),
                                     headers={'Authorization': 'Bearer ' + api_key,
                                              'Content-Type': 'application/json'}, method='POST')
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.load(response)
    content = data['choices'][0]['message']['content']
    if not isinstance(content, str) or not content.strip():
        raise ValueError('API returned empty or unsupported response')
    return {'id': req['id'], 'answer': content, 'usage': data.get('usage'),
            'elapsed_seconds': round(time.monotonic() - started, 3)}


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def execute(args):
    cases = json.loads((HERE / 'cases.json').read_text(encoding='utf-8'))
    skill = SKILL.read_text(encoding='utf-8')
    if len(cases) != 10 or len({c['id'] for c in cases}) != 10:
        raise ValueError('Expected exactly 10 uniquely identified cases')
    if args.mode == 'run' and (not args.model or not os.environ.get('OPENAI_API_KEY')):
        raise ValueError('run requires --model and OPENAI_API_KEY; no request sent')
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    reqs = build_requests(cases, skill, args.seed)
    manifest = {'mode': args.mode, 'model': args.model, 'seed': args.seed,
                'n_cases': len(cases), 'n_arms': len(ARMS), 'n_requests': len(reqs),
                'created_utc': datetime.now(timezone.utc).isoformat(),
                'dataset_sha256': hashlib.sha256((HERE / 'cases.json').read_bytes()).hexdigest(),
                'temperature': 0, 'tools': 'disabled',
                'skill_sha256': hashlib.sha256(skill.encode()).hexdigest(),
                'note': 'dry-run creates no model answers' if args.mode == 'dry-run' else 'review blinded before unmasking'}
    write_json(out / 'manifest.json', manifest)
    write_json(out / 'key.json', {r['id']: {'case_id': r['case_id'], 'arm': r['arm']} for r in reqs})
    with (out / 'requests.jsonl').open('w', encoding='utf-8') as f:
        for req in reqs:
            f.write(json.dumps(req, ensure_ascii=False) + '\n')
    if args.mode == 'dry-run':
        print(f'Prepared {len(reqs)} requests; no model was called. Output: {out}')
        return
    api_key = os.environ['OPENAI_API_KEY']
    with (out / 'raw.jsonl').open('w', encoding='utf-8') as raw, (out / 'blind.jsonl').open('w', encoding='utf-8') as blind:
        for index, req in enumerate(reqs, 1):
            result = call_api(args.url, args.model, api_key, req, args.timeout)
            raw.write(json.dumps(result, ensure_ascii=False) + '\n')
            raw.flush()
            masked = {'id': req['id'], 'case_id': req['case_id'], 'question': req['question'], 'answer': result['answer']}
            blind.write(json.dumps(masked, ensure_ascii=False) + '\n')
            blind.flush()
            print(f'{index}/{len(reqs)} completed', flush=True)
    with (out / 'scores.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'accuracy', 'problem', 'mechanism', 'boundary', 'clarity', 'major_error', 'notes'])
        for r in reqs:
            writer.writerow([r['id'], '', '', '', '', '', '', ''])
    print('Blind answers and blank scores are ready. Do not open key.json until grading is finished.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['dry-run', 'run'], required=True)
    parser.add_argument('--out', required=True, help='new output directory; never overwritten')
    parser.add_argument('--model', help='required for run')
    parser.add_argument('--url', default='https://api.openai.com/v1/chat/completions')
    parser.add_argument('--seed', default='theo-lens-v1')
    parser.add_argument('--timeout', type=int, default=120)
    args = parser.parse_args()
    try:
        execute(args)
    except (ValueError, OSError, KeyError, urllib.error.URLError) as error:
        parser.exit(1, 'Experiment stopped: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
