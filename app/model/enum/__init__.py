# encoding: utf-8
from enum import Enum


class StatusEnum(Enum):
    disabled = 0
    enabled = 1
    deleted = 2
    inactive = 3


class BooleanEnum(Enum):
    false = 0
    true = 1


class AddressTypeEnum(Enum):
    home = 0
    contact = 1
    comercial = 2


class PhoneTypeEnum(Enum):
    home = 0
    contact = 1
    comercial = 2
    mobile = 3


class StatusApiKeyEnum(Enum):
    disabled = 0
    enabled = 1
    revoked = 2
    expired = 3


class ReadWriteAccessEnum(Enum):
    none = 0
    read = 1
    write = 2


class FileTypeEnum(Enum):
    document = 0
    photo_profile = 1


class FileSubTypeEnum(Enum):
    photo_profile = 0
    rg = 1
    cnh = 2
    address = 3
    cpf = 4
    selfie = 5
    cnh_front = 6
    cnh_back = 7
    rg_front = 8
    rg_back = 9


class MaritalStatusEnum(Enum):
    single = 0
    married = 1
    widower = 2
    divorced = 3


class TokenSourceEnum(Enum):
    partner = 0
    client = 1
    manager = 2
    system = 3


class TokenStatusEnum(Enum):
    active = 0
    revoked = 1
    disabled = 2
    deleted = 3


class ClientSignupStatus(Enum):
    incomplete = 0
    complete = 1
    ready = 2
    bank_send = 3
    bank_error = 4
    bank_success = 5
    bank_approve = 6
    fixed = 7


class ClientBrokerSignupStatus(Enum):
    none = 0
    ready = 1
    broker_send = 2
    broker_error = 3
    broker_success = 4

class ClientExchangeSignupStatus(Enum):
    none = 0
    ready = 1
    exchange_send = 2
    exchange_error = 3
    exchange_success = 4


class SuitabilityTypeEnum(Enum):
    cvm = 0
    dna = 1
    personality = 2


class SettingTypeEnum(Enum):
    dashboard = 0
    screen = 1
    news = 2


class NewsTypeEnum(Enum):
    private = 0
    shared = 1


class MessageStatusEnum(Enum):
    new = 0
    shown = 1
    hidden = 2
    deleted = 3
    archived = 4


class MessagePriorityEnum(Enum):
    normal = 0
    high = 1
    low = 2


class AccountTypeEnum(Enum):
    main_account = 0
    sub_account = 1


class AccountFavoriteTypeEnum(Enum):
    physical_account = 0
    pix = 1


class ThirdPartyTransactionCategoryEnum(Enum):
    nao_classificado = 0
    moradia = 1
    saude = 2
    transporte = 3
    mercado = 4
    educacao = 5
    pagamento_de_cartao = 6


class ThirdPartyTransactionReportTypeEnum(Enum):
    credit_card = 0
    debit = 1


class CrediGoTransactionReportTypeEnum(Enum):
    credit_card = 0
    debit = 1
    investment = 2


class CrediGoConnectionTypeEnum(Enum):
    bank = 0
    broker = 1
    credit_card = 2


class PaymentScheduleTypeEnum(Enum):
    boleto = 0
    doc = 1
    ted = 2
    pix = 3
    internal_transfer = 4


class StatementCategoryTypeEnum(Enum):
    expense = 0
    revenue = 1


class OnboardingStatusEnum(Enum):
    new = 0
    send_to_bank = 1
    intenal_analysis = 2
    bank_analysis = 3
    manual_analisis = 4
    bank_error = 5
    bank_success = 6
    complete = 7


class LoanTaxPeriodTypeEnum(Enum):
    daily = 0
    weekly = 1
    monthly = 2
    yearly = 3


class NotificationDeviceEnum(Enum):
    web = 0
    android = 1
    ios = 2


class LoanTypeEnum(Enum):
    real_state = 0
    car = 1
    personal = 2
    p2p = 3


class LoanModalityEnum(Enum):
    acquisition_other_things_pre = 0, 'AQUISIÇÃO DE OUTROS BENS - PRÉ-FIXADO'
    acquisition_vehicle_pre = 1, 'AQUISIÇÃO DE VEÍCULOS - PRÉ-FIXADO'
    lease_mercantil_vehicle_pre = 2, 'ARRENDAMENTO MERCANTIL DE VEÍCULOS - PRÉ-FIXADO'
    credit_card_installment_pre = 3, 'CARTÃO DE CRÉDITO - PARCELADO - PRÉ-FIXADO'
    credit_card_overdue_pre = 4, 'CARTÃO DE CRÉDITO - ROTATIVO EM ATRASO - PRÉ-FIXADO'
    credit_card_normal_pre = 5, 'CARTÃO DE CRÉDITO - ROTATIVO EM CURSO NORMAL - PRÉ-FIXADO'
    credit_card_total_pre = 6, 'CARTÃO DE CRÉDITO - ROTATIVO TOTAL - PRÉ-FIXADO'
    overdraft_pre = 7, 'CHEQUE ESPECIAL - PRÉ-FIXADO'
    consigned_credit_inss_pre = 8, 'CRÉDITO PESSOAL CONSIGNADO INSS - PRÉ-FIXADO'
    consigned_credit_private_pre = 9, 'CRÉDITO PESSOAL CONSIGNADO PRIVADO - PRÉ-FIXADO'
    consigned_credit_public_pre = 10, 'CRÉDITO PESSOAL CONSIGNADO PÚBLICO - PRÉ-FIXADO'
    credit_pre = 11, 'CRÉDITO PESSOAL NÃO-CONSIGNADO - PRÉ-FIXADO'
    check_cashing_pre = 12, 'DESCONTO DE CHEQUES - PRÉ-FIXADO'
    house_financing_market_rate_ipca = 13, 'FINANCIAMENTO IMOBILIÁRIO COM TAXAS DE MERCADO - PÓS-FIXADO REFERENCIADO EM IPCA'
    house_financing_market_rate_tr  = 14, 'FINANCIAMENTO IMOBILIÁRIO COM TAXAS DE MERCADO - PÓS-FIXADO REFERENCIADO EM TR'
    house_financing_market_rate_pre  = 15,'FINANCIAMENTO IMOBILIÁRIO COM TAXAS DE MERCADO - PRÉ-FIXADO'
    house_financing_regulated_rate_ipca = 16, 'FINANCIAMENTO IMOBILIÁRIO COM TAXAS REGULADAS - PÓS-FIXADO REFERENCIADO EM IPCA'
    house_financing_regulated_rate_tr = 17, 'FINANCIAMENTO IMOBILIÁRIO COM TAXAS REGULADAS - PÓS-FIXADO REFERENCIADO EM TR'
    house_financing_regulated_rate_pre  = 18,'FINANCIAMENTO IMOBILIÁRIO COM TAXAS REGULADAS - PRÉ-FIXADO'

    def __new__(cls, value, desc):
        member = object.__new__(cls)
        member._value_ = value
        member.description = desc
        return member

    def __int__(self):
        return self.value


class PlanFeatureTypeEnum(Enum):
    undefined = 0, 'Não definido'
    bank_account_monitor = 1, 'Monitoramento de contas bancárias'
    budget_control = 2, 'Controle de orçamento'
    life_situations = 3, 'Situaçõe de vida'
    life_goals = 4, 'Objetivos de vida'
    patrimony = 5, 'Patrimônio'
    income_planning = 6, 'Planejamento de receitas'
    qty_account_planning = 7, 'Número de contas de planejamento'
    autopilot = 8, 'Piloto automático'
    send_orders = 9, 'Envio de ordens'
    qty_broker_connected = 10, 'Quantidade de corretoras integradas'
    qty_investment_theme = 11, 'Quantidade de temas de investimentos'
    qty_optimize_daily = 12, 'Quantidade de otimizações diárias'
    qty_optimize_weekly = 13, 'Quantidade de otimizações semanais'
    qty_optimize_monthly = 14, 'Quantidade de otimizações mensais'
    future_forecast  = 15, 'Previsão futura'
    performance_analysis_history  = 16, 'Análise de performance historica'
    performance_analysis_actual = 17, 'Análise de performance atual'
    performance_analysis_future = 18, 'Análise de performance futura'
    cryptocurrencies  = 19, 'Criptomoedas'
    international_market_assets  = 20,'Ativos no mercado internacional'
    open_banking = 21, 'Open Banking'
    qty_free_cards = 22, 'Cartões gratuítos'

    def __new__(cls, value, desc):
        member = object.__new__(cls)
        member._value_ = value
        member.description = desc
        return member

    def __int__(self):
        return self.value

class PlanFeatureValueTypeEnum(Enum):
    undefined = 0
    boolean = 1
    int = 2
    float = 3
    string = 4
    date = 5