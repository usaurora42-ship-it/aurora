# encoding: utf-8
import requests
from flask import jsonify, request
from app.blueprints.site import SiteBlueprint

CEP_ORIGEM     = '38413162'
PESO_GRAMAS    = 300
ALTURA_CM      = 5
LARGURA_CM     = 15
COMPRIMENTO_CM = 20

MELHOR_ENVIO_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZDFlYWIwMGJmMzkzNTY3Y2ViZjNiYTIyN2YwODI4ZGQzMDhiY2Y2NGQ1MTkzYjdmY2YyMzBkNGE0MzUwMjlkZjZjOWMxY2RmOTc5YjA5YjYiLCJpYXQiOjE3Nzc1NzIxNjguMDMwNzAxLCJuYmYiOjE3Nzc1NzIxNjguMDMwNzAyLCJleHAiOjE4MDkxMDgxNjguMDE1ODgzLCJzdWIiOiJhMWFiMTMyZi00M2VmLTQ2NGMtOTIxMy1mYjc0ZTRkNTBjNjQiLCJzY29wZXMiOlsic2hpcHBpbmctY2FsY3VsYXRlIl19.xVRwrvRP1T52VO7dyuyTlZXomoxBauAuUMe810LW3upxYMg_sMt_Hgob0PKfQKaQk-7T9ijeBTkT---i8Ovl3lGbdnmP8v6ZDPGcW02_13bhK1hDjZkFg6kJQjhRkLOu9KUUv77izlvGknuqcDJK3QN139mzk9hS8qfpJeZoVV_EJtEmnVPZz1k0fbGpgA2fOmZfvcidXsCOIUD_0FUF8axG2V_gXTmRACRVQCX_TWCIKGrkAKbYjeLyFgA-wwDB5Nzme0nNO1IAQ3-fEZyNnKWIy6Yz2-TbGHrgvz2vJJEBsMQsyNnV9Z-kT3ZVvYCzktmGve_fgEEOROCNalSt5lpw3OfuIOk78uSRwivFtyQdDvGMAky0s7Yw5uKD_zx3TVBiVx7D58NewpFp2o-tKvWHmnUePBHQDOtty6sep-p4F-RBhai22UDt2OVqq7MB7LofzybklLn5Lc2KOC1bxIdtPt3pwvlPX6jxePrWofgiC6xzBRBpXZSUxlXL5NQmrs1wqu7jaH52zA1sJMl6IU7HAIYHJtRHE4SMe-_fOxy1SWqq3eCmpQdvti0BPz6u7SNweSHIlUH3dIRg3lUhaY1GIlY6xvtji5fZmR6oO5-tXC6EO8mvCWkaFuCBYKO3BVW__7bbP-JX8vZY4wH_6T07r_A14gWUQ4XsJ53cVsc'

SERVICOS = [
    {'id': 1, 'nome': 'PAC',   'key': 'pac'},
    {'id': 2, 'nome': 'SEDEX', 'key': 'sedex'},
]


@SiteBlueprint.route('/cart/frete', methods=['GET'])
def calcular_frete():
    """Calcula PAC e SEDEX via API Melhor Envio."""
    cep_destino = request.args.get('cep', '').replace('-', '').strip()

    if len(cep_destino) != 8 or not cep_destino.isdigit():
        return jsonify({'success': False, 'erro': 'CEP inválido'})

    try:
        payload = {
            'from': {'postal_code': CEP_ORIGEM},
            'to':   {'postal_code': cep_destino},
            'package': {
                'height': ALTURA_CM,
                'width':  LARGURA_CM,
                'length': COMPRIMENTO_CM,
                'weight': PESO_GRAMAS / 1000,
            },
            'services': ','.join(str(s['id']) for s in SERVICOS),
            'options': {
                'insurance_value': 0,
                'receipt':         False,
                'own_hand':        False,
            }
        }

        resp = requests.post(
            'https://melhorenvio.com.br/api/v2/me/shipment/calculate',
            json=payload,
            headers={
                'Authorization': f'Bearer {MELHOR_ENVIO_TOKEN}',
                'Content-Type':  'application/json',
                'Accept':        'application/json',
                'User-Agent':    'Aurora Semijóias (contato@aurora.com.br)',
            },
            timeout=10
        )
        resp.raise_for_status()
        resultados = resp.json()

        resultado = {}
        for r in resultados:
            name = (r.get('name') or '').upper()
            if 'PAC' in name:
                key = 'pac'
            elif 'SEDEX' in name:
                key = 'sedex'
            else:
                continue

            if r.get('error'):
                resultado[key] = {'erro': r['error']}
            else:
                valor = r.get('price')
                prazo = r.get('delivery_time', '?')
                if valor is not None:
                    resultado[key] = {
                        'valor': f'{float(valor):.2f}'.replace('.', ','),
                        'prazo': str(prazo),
                    }

        if not resultado:
            return jsonify({'success': False, 'erro': 'Nenhum serviço disponível'})

        return jsonify({'success': True, **resultado})

    except Exception as e:
        return jsonify({'success': False, 'erro': str(e), 'tipo': type(e).__name__})
