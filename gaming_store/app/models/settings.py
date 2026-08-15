from datetime import datetime
from app import db


class SiteSettings(db.Model):
    __tablename__ = 'site_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get(key, default=None):
        setting = SiteSettings.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set(key, value, description=None):
        setting = SiteSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = SiteSettings(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting

    def __repr__(self):
        return f'<SiteSettings {self.key}: {self.value}>'


class PaymentSettings(db.Model):
    __tablename__ = 'payment_settings'

    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(100))
    account_title = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    iban = db.Column(db.String(50))
    # Mobile wallets (Easypaisa / JazzCash)
    easypaisa_number = db.Column(db.String(50))
    jazzcash_number = db.Column(db.String(50))
    mobile_wallet_name = db.Column(db.String(50))
    mobile_wallet_number = db.Column(db.String(50))
    instructions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_active():
        return PaymentSettings.query.filter_by(is_active=True).first()

    def __repr__(self):
        return f'<PaymentSettings {self.bank_name}>'
