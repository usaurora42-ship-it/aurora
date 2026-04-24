# encoding: utf-8
"""
Gerador de QR Code PIX - Padrão Banco Central do Brasil (EMV)
Suporta qualquer tipo de chave: CPF, CNPJ, telefone, email, chave aleatória
"""
import qrcode
import io
import base64


# ── Configurações da loja (edite aqui) ──
PIX_KEY       = '05883206689'  # sua chave PIX
PIX_KEY_TYPE  = 'cpf'                       # cpf | cnpj | telefone | email | aleatoria
PIX_NAME      = 'Amora Platter Box'           # nome do recebedor (max 25 chars)
PIX_CITY      = 'Uberlandia'                  # cidade do recebedor (sem acentos, max 15 chars)


def _crc16(data: str) -> str:
    """Calcula o CRC16 CCITT-FALSE exigido pelo padrão EMV PIX."""
    crc = 0xFFFF
    for byte in data.encode('utf-8'):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return format(crc, '04X')


def _field(id: str, value: str) -> str:
    """Formata um campo EMV: ID + tamanho + valor."""
    return f'{id}{len(value):02d}{value}'


def gerar_payload_pix(valor: float, txid: str = '***', descricao: str = '') -> str:
    """
    Gera o payload PIX no padrão EMV/QR Code do Banco Central.

    Args:
        valor:     Valor do pagamento (ex: 25.90)
        txid:      Identificador da transação (max 25 chars). Use '***' para não fixar.
        descricao: Descrição opcional (max 72 chars)

    Returns:
        String do payload pronta para gerar QR Code ou Copia e Cola
    """
    chave = PIX_KEY.strip()
    nome  = PIX_NAME[:25].strip()
    cidade = PIX_CITY[:15].strip()
    txid  = (txid or '***')[:25]

    # ── Merchant Account Info (ID 26) ──
    gui     = _field('00', 'BR.GOV.BCB.PIX')
    chave_f = _field('01', chave)
    info26  = gui + chave_f
    if descricao:
        info26 += _field('02', descricao[:72])
    mai = _field('26', info26)

    # ── Payload Format Indicator ──
    pfi = _field('00', '01')

    # ── Point of Initiation Method ──
    # 11 = QR estático | 12 = QR dinâmico (apenas uma vez)
    poi = _field('01', '12' if txid != '***' else '11')

    # ── Merchant Category Code ──
    mcc = _field('52', '0000')

    # ── Transaction Currency (986 = BRL) ──
    cur = _field('53', '986')

    # ── Transaction Amount ──
    amt = _field('54', f'{valor:.2f}')

    # ── Country Code ──
    cc = _field('58', 'BR')

    # ── Merchant Name ──
    mn = _field('59', nome)

    # ── Merchant City ──
    mc = _field('60', cidade)

    # ── Additional Data Field (ID 62) — txid ──
    txid_f = _field('05', txid)
    adf    = _field('62', txid_f)

    # ── Monta payload sem CRC ──
    payload = pfi + poi + mai + mcc + cur + amt + cc + mn + mc + adf

    # ── CRC16 (ID 63, sempre 4 chars) ──
    payload += '6304'
    payload += _crc16(payload)

    return payload


def gerar_qrcode_base64(payload: str) -> str:
    """
    Gera o QR Code como imagem base64 para exibir diretamente no HTML.

    Returns:
        String base64 da imagem PNG (use em <img src="data:image/png;base64,...">)
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color='#1a1208', back_color='white')

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def gerar_pix(valor: float, txid: str = '***', descricao: str = '') -> dict:
    """
    Função principal — retorna tudo que o template precisa.

    Returns:
        dict com:
            payload    → código Copia e Cola
            qrcode_b64 → imagem base64 do QR Code
            valor_fmt  → valor formatado (ex: "R$ 25,90")
    """
    payload    = gerar_payload_pix(valor, txid, descricao)
    qrcode_b64 = gerar_qrcode_base64(payload)

    return {
        'payload':    payload,
        'qrcode_b64': qrcode_b64,
        'valor_fmt':  f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    }
