# knowledge_base.py
# ─────────────────────────────────────────────────────────────────
# NeoBank comprehensive knowledge base used by the RAG engine.
# Each document has: id, category, title, content, tags.
# This file is the single source of truth for all bank policy Q&A.
# ─────────────────────────────────────────────────────────────────

DOCUMENTS = [

    # ── ABOUT NEOBANK ──────────────────────────────────────────────
    {
        "id": "about_001",
        "category": "about",
        "title": "About NeoBank",
        "content": """
NeoBank is a modern digital banking institution founded in 2020, headquartered in Mumbai, India.
We serve over 2 million customers across India with a full suite of banking services delivered
entirely through our digital platform. NeoBank is licensed by the Reserve Bank of India (RBI)
and regulated under the Banking Regulation Act, 1949.

Our mission is to make banking accessible, transparent, and rewarding for every Indian.
We believe banking should be simple — no hidden fees, no confusing terms, no branch queues.

Core values: Transparency, Security, Innovation, Customer-First.

NeoBank offers: Savings Accounts, Checking Accounts, Premium Accounts, Fixed Deposits,
Personal Loans, Instant Transfers, UPI Integration, International Wire Transfers,
Debit Cards, and 24/7 AI-powered banking support.

Awards: Best Digital Bank India 2022, 2023 (Banking Technology Awards),
Fastest Growing Fintech 2023 (Economic Times), RBI RegTech Innovation Award 2023.

NeoBank is a member of Deposit Insurance and Credit Guarantee Corporation (DICGC),
which insures deposits up to ₹5,00,000 per depositor per bank.
        """,
        "tags": ["about", "neobank", "history", "mission", "rbi", "license"]
    },

    # ── ACCOUNT TYPES ──────────────────────────────────────────────
    {
        "id": "acc_savings_001",
        "category": "accounts",
        "title": "Savings Account",
        "content": """
NeoBank Savings Account is designed for individuals who want to grow their money safely
while keeping it accessible.

ELIGIBILITY: Indian residents aged 18 and above. Minors (10-17) with guardian co-applicant.
NRIs with valid documents.

INTEREST RATE: 4.5% per annum, compounded quarterly. Interest credited every quarter
(March, June, September, December). Rate reviewed periodically based on RBI repo rate.

MINIMUM BALANCE:
- Digital Savings (Zero Balance): ₹0 minimum — no penalties ever.
- Classic Savings: ₹1,000 average monthly balance.
- Premium Savings: ₹10,000 average monthly balance.

FEATURES:
- Free NEFT/IMPS/RTGS up to 5 transactions per month
- Free UPI transactions (unlimited)
- Debit card with ₹40,000 daily ATM withdrawal limit
- Free cheque book (25 leaves per year)
- Nomination facility
- Auto-sweep to Fixed Deposit above ₹25,000

DOCUMENTS REQUIRED TO OPEN:
- PAN Card (mandatory)
- Aadhaar Card for e-KYC
- Passport-size photograph
- Address proof (Aadhaar/Passport/Utility Bill)
- Video KYC via app (takes 5 minutes)

BENEFITS:
- No account maintenance fees for Digital Savings
- Instant account activation
- Virtual debit card issued immediately
- Physical debit card delivered in 5-7 working days
        """,
        "tags": ["savings", "account", "interest", "minimum balance", "zero balance", "debit card"]
    },

    {
        "id": "acc_checking_001",
        "category": "accounts",
        "title": "Checking Account (Current Account)",
        "content": """
NeoBank Checking Account (Current Account) is designed for individuals and businesses
with high transaction volumes. Ideal for freelancers, small businesses, and professionals.

ELIGIBILITY: Indian residents and businesses with valid GST/business registration.
Minimum age: 18 years. Proprietorships, partnerships, and private limited companies eligible.

INTEREST RATE: No interest on checking accounts (standard banking practice).
However, idle balances above ₹50,000 are auto-swept to a linked savings account at 4.5% p.a.

MINIMUM BALANCE:
- Individual Checking: ₹5,000 average monthly balance
- Business Checking: ₹10,000 average monthly balance
- Penalty for non-maintenance: ₹200 per month (individual), ₹500 per month (business)

TRANSACTION LIMITS:
- Daily debit: Up to ₹10,00,000
- NEFT: Unlimited free transactions
- RTGS: Unlimited free transactions above ₹2 lakh
- Cheque issuance: Unlimited (cheque book free for first 50 leaves/year)

FEATURES:
- Overdraft facility up to 3× average monthly balance (subject to approval)
- Multi-user access for businesses (up to 5 sub-users)
- API banking integration for businesses
- Dedicated relationship manager for balances above ₹5 lakh
- GST invoicing and payment integration
- Bulk payment facility (payroll, vendor payments)

DOCUMENTS FOR BUSINESS ACCOUNT:
- Certificate of Incorporation / Partnership Deed
- GST Registration Certificate
- Board Resolution / Authorization Letter
- KYC of all directors/partners
        """,
        "tags": ["checking", "current account", "business", "overdraft", "transaction limits"]
    },

    {
        "id": "acc_premium_001",
        "category": "accounts",
        "title": "Premium Account",
        "content": """
NeoBank Premium Account is our flagship offering for high-net-worth individuals who demand
the best in banking services, personalised attention, and exclusive benefits.

ELIGIBILITY: Minimum ₹5,00,000 average quarterly balance OR monthly salary credit of ₹1,50,000+
OR total relationship value (all NeoBank products) above ₹10,00,000.

INTEREST RATE:
- Savings portion: 5.5% per annum (1% higher than standard)
- Fixed Deposit portion (auto-sweep): Up to 7.5% p.a.

FEATURES AND BENEFITS:
- Dedicated Relationship Manager (RM) — personal mobile/WhatsApp access
- Complimentary airport lounge access (8 visits/year domestically, 4 internationally)
- Premium Platinum Debit Card with ₹2,00,000 daily ATM limit
- Zero forex markup on international transactions
- Free demand drafts (unlimited)
- Priority customer service — 30-second call answer guarantee
- Free safe deposit locker (subject to availability at partner banks)
- Complimentary personal accident insurance: ₹50,00,000 cover
- Free travel insurance for international trips
- Concierge services (travel bookings, restaurant reservations, event tickets)
- Quarterly portfolio review with wealth management team
- Exclusive investment products: Curated mutual funds, PMS, AIFs

PREMIUM DEBIT CARD BENEFITS:
- 5× reward points on all spends
- 10× reward points on dining and travel
- Milestone bonus: 10,000 points on ₹1,00,000 monthly spend
- Reward points redeemable against statement credit (1 point = ₹0.25)
- Complimentary golf rounds (4/year at partner courses)

DOWNGRADE POLICY: If balance falls below eligibility for 2 consecutive quarters,
account is downgraded to Classic Savings with 30-day advance notice.
        """,
        "tags": ["premium", "platinum", "high net worth", "relationship manager", "lounge", "rewards"]
    },

    # ── FEES ────────────────────────────────────────────────────────
    {
        "id": "fees_atm_001",
        "category": "fees",
        "title": "ATM Fees and Charges",
        "content": """
NeoBank ATM FEE STRUCTURE (effective April 2024):

FREE ATM TRANSACTIONS:
- NeoBank ATMs: Unlimited free transactions (withdrawals + balance enquiry)
- Other bank ATMs in India: 5 free transactions per month
  (applies to both financial and non-financial transactions combined)
- After free limit: ₹21 + GST per financial transaction, ₹10 + GST per non-financial

PREMIUM ACCOUNT ATM:
- NeoBank ATMs: Unlimited free
- Other bank ATMs: 10 free per month
- After limit: ₹15 + GST per financial transaction

INTERNATIONAL ATM WITHDRAWALS:
- Standard/Classic accounts: ₹150 + 3.5% forex markup per transaction
- Premium accounts: ₹100 + 0% forex markup (zero markup benefit)
- Currency conversion: VISA/Mastercard rate + markup applied

DAILY WITHDRAWAL LIMITS BY ACCOUNT TYPE:
- Digital Savings (Zero Balance): ₹20,000 per day
- Classic Savings: ₹40,000 per day
- Checking Account: ₹1,00,000 per day
- Premium Account: ₹2,00,000 per day

ATM CARD REPLACEMENT:
- Lost/stolen card replacement: ₹200 + GST
- Damaged card replacement: ₹150 + GST
- Express delivery (48 hours): Additional ₹150

IMPORTANT NOTES:
- ATM fees are debited from account at end of month
- GST of 18% applicable on all fee amounts
- Failed ATM transactions due to insufficient funds are NOT counted in free limit
- Transactions at NeoBank partner ATMs (HDFC, ICICI WhiteLabel ATMs) count as NeoBank ATMs
        """,
        "tags": ["atm", "fees", "withdrawal", "daily limit", "international", "free transactions"]
    },

    {
        "id": "fees_transaction_001",
        "category": "fees",
        "title": "Transaction Fees and Charges",
        "content": """
NeoBank TRANSACTION FEE SCHEDULE:

NEFT (National Electronic Funds Transfer):
- Outward NEFT via app/internet banking: FREE (unlimited)
- NEFT via branch: ₹2.50 to ₹25 depending on amount (branch charges extra)
- Inward NEFT: Always FREE
- Processing time: Near real-time (RBI NEFT available 24×7)

IMPS (Immediate Payment Service):
- Up to ₹5,000: FREE via app
- ₹5,001 to ₹1,00,000: FREE via app
- ₹1,00,001 to ₹2,00,000: ₹15 + GST
- ₹2,00,001 to ₹5,00,000: ₹25 + GST
- Premium accounts: ALL IMPS FREE

RTGS (Real Time Gross Settlement) — minimum ₹2 lakh:
- ₹2 lakh to ₹5 lakh: ₹25 + GST via app
- Above ₹5 lakh: ₹50 + GST via app
- Branch RTGS: Additional ₹50 service charge
- Premium accounts: ALL RTGS FREE

UPI TRANSACTIONS: 100% FREE — no charges ever for any UPI transaction.

INTERNAL TRANSFER (NeoBank to NeoBank): 100% FREE — always.

INTERNATIONAL WIRE TRANSFER (SWIFT):
- Outward remittance: ₹500 + correspondent bank charges
- Forex markup: 3.5% (standard), 0% (premium)
- Minimum amount: ₹5,000 equivalent
- Processing time: 2-5 business days

CHEQUE CHARGES:
- Outstation cheque collection: ₹50 per cheque
- Cheque bounce (outward): ₹500 per instance
- Cheque bounce (inward): ₹300 per instance
- Stop payment instruction: ₹100 per cheque

DEMAND DRAFT:
- Up to ₹10,000: ₹30
- ₹10,001 to ₹1 lakh: ₹50
- Above ₹1 lakh: ₹100
- Premium accounts: FREE

STATEMENT CHARGES:
- Digital statement: FREE (anytime via app)
- Email statement: FREE
- Physical statement: ₹50 per statement (last 6 months)
- Duplicate physical statement: ₹100
        """,
        "tags": ["neft", "imps", "rtgs", "upi", "wire transfer", "fees", "charges", "transaction"]
    },

    {
        "id": "fees_maintenance_001",
        "category": "fees",
        "title": "Account Maintenance Fees",
        "content": """
NeoBank ACCOUNT MAINTENANCE FEE STRUCTURE:

DIGITAL SAVINGS ACCOUNT (ZERO BALANCE):
- Account maintenance fee: ₹0 (completely free forever)
- No minimum balance requirement
- No non-maintenance penalty
- SMS alerts: ₹15/quarter (optional, can disable)
- Email alerts: FREE

CLASSIC SAVINGS ACCOUNT:
- Monthly maintenance fee: ₹0 if average monthly balance ≥ ₹1,000
- Non-maintenance fee: ₹50 per month if balance below ₹1,000
- Annual account fee: ₹0

CHECKING ACCOUNT (INDIVIDUAL):
- Monthly maintenance: ₹0 if average balance ≥ ₹5,000
- Non-maintenance penalty: ₹200 per month
- Annual account fee: ₹0

PREMIUM ACCOUNT:
- Account maintenance: ₹0 (all fees waived)
- Relationship fee: ₹0 (relationship manager included free)
- Annual premium fee: ₹0 as long as eligibility maintained

OTHER CHARGES:
- Account closure within 6 months of opening: ₹500
- Account closure after 6 months: FREE
- Dormant account activation: ₹100 (account dormant after 24 months of no transactions)
- Account reactivation after freeze: ₹200

DEBIT CARD ANNUAL FEE:
- Virtual debit card: FREE always
- Classic physical debit card: ₹200/year (waived first year)
- Premium Platinum debit card: ₹999/year (waived if spend ≥ ₹1,00,000/year)

SMS ALERT PRICING:
- Transaction alerts: ₹15 per quarter (₹60/year) — optional
- Balance alerts: Included in transaction alert package
- Login/OTP alerts: FREE always (security alerts cannot be disabled)
        """,
        "tags": ["maintenance", "fees", "charges", "debit card", "annual fee", "zero balance"]
    },

    # ── LIMITS ─────────────────────────────────────────────────────
    {
        "id": "limits_daily_001",
        "category": "limits",
        "title": "Daily Transaction Limits",
        "content": """
NeoBank DAILY TRANSACTION LIMITS:

DIGITAL SAVINGS (ZERO BALANCE):
- ATM cash withdrawal: ₹20,000/day
- UPI per transaction: ₹1,00,000 (NPCI limit)
- UPI daily: ₹2,00,000
- IMPS/NEFT single transaction: ₹2,00,000
- NEFT daily: ₹5,00,000
- Debit card POS: ₹50,000/day
- Online shopping: ₹1,00,000/day

CLASSIC SAVINGS:
- ATM: ₹40,000/day
- UPI daily: ₹5,00,000
- IMPS/NEFT single: ₹5,00,000
- NEFT daily: ₹10,00,000
- Debit card POS: ₹1,00,000/day
- Online shopping: ₹2,00,000/day

CHECKING ACCOUNT:
- ATM: ₹1,00,000/day
- NEFT daily: ₹50,00,000
- RTGS: No daily limit (transaction limits apply)
- Debit card POS: ₹5,00,000/day

PREMIUM ACCOUNT:
- ATM: ₹2,00,000/day
- UPI daily: ₹10,00,000 (special NPCI higher limit for premium)
- NEFT daily: ₹1,00,00,000 (1 crore)
- RTGS: No daily limit
- Debit card POS: ₹10,00,000/day
- International POS: Unlimited (subject to card scheme limits)

LIMIT ENHANCEMENT:
Customers can request temporary or permanent limit enhancement via:
1. App → Settings → Transaction Limits → Request Enhancement
2. Customer care (1800-NEOBANK)
3. Requires re-KYC for enhancements above 2× current limit
Standard processing: 2 hours for temporary (24-72 hours), 2 business days for permanent.
        """,
        "tags": ["daily limit", "transaction limit", "upi", "atm", "neft", "enhancement"]
    },

    {
        "id": "limits_monthly_001",
        "category": "limits",
        "title": "Monthly Transaction Limits",
        "content": """
NeoBank MONTHLY TRANSACTION LIMITS:

DIGITAL SAVINGS:
- Total monthly debit transactions: ₹20,00,000
- Cash withdrawals (ATM+branch): ₹60,000/month
- International transactions: ₹2,00,000/month
- Cheque payments: ₹5,00,000/month

CLASSIC SAVINGS:
- Total monthly debit: ₹50,00,000
- Cash withdrawals: ₹1,50,000/month
- International: ₹5,00,000/month

CHECKING ACCOUNT:
- Total monthly debit: ₹5,00,00,000 (5 crore)
- Cash withdrawals: ₹5,00,000/month
- International: ₹20,00,000/month

PREMIUM ACCOUNT:
- Total monthly debit: No limit (KYC-compliant)
- Cash withdrawals: ₹10,00,000/month
- International: ₹50,00,000/month

SPECIAL MONTHLY RULES:
- Large cash deposits above ₹50,000 require PAN declaration
- Aggregate deposits above ₹10,00,000 in financial year reported to Income Tax per Form 61A
- Foreign remittances above $2,50,000 per year require RBI LRS declaration
- Suspicious transaction reporting: Transactions flagged by our ML system reviewed within 24 hours

LIMIT RESET: All monthly limits reset on the 1st of each calendar month at 00:00 IST.
        """,
        "tags": ["monthly limit", "cash withdrawal", "international", "income tax", "lrs"]
    },

    # ── SECURITY ───────────────────────────────────────────────────
    {
        "id": "security_auth_001",
        "category": "security",
        "title": "Authentication and Security",
        "content": """
NeoBank AUTHENTICATION SYSTEM:

LOGIN SECURITY:
- 6-digit MPIN for app login (setup during onboarding)
- Biometric authentication: Fingerprint and Face ID supported
- SMS OTP: 6-digit, valid for 10 minutes
- Email OTP: For sensitive operations
- Device binding: App bound to registered device
- Maximum login attempts: 5 before 30-minute lockout; 10 before 24-hour lockout

TWO-FACTOR AUTHENTICATION (2FA):
- All logins require SMS OTP on new/unrecognized devices
- High-value transactions (above ₹50,000) always require 2FA
- International transactions always require 2FA
- New payee addition requires both OTP and 24-hour cooling period

SESSION MANAGEMENT:
- Auto-logout after 5 minutes of inactivity (configurable: 2-15 minutes)
- Maximum concurrent sessions: 2 (mobile + web)
- Session token expires every 24 hours
- Device management: View and remotely logout all sessions from app

MPIN POLICY:
- Must be 6 digits, cannot be sequential (123456) or repeated (111111)
- Change mandatory every 180 days
- Cannot reuse last 5 MPINs
- Forgotten MPIN: Reset via biometric + OTP (no branch visit needed)

PASSWORD POLICY (Web Banking):
- Minimum 8 characters
- Must contain: uppercase, lowercase, number, special character
- Change every 90 days mandatory
- Cannot reuse last 5 passwords
        """,
        "tags": ["authentication", "mpin", "2fa", "otp", "login", "session", "security"]
    },

    {
        "id": "security_encryption_001",
        "category": "security",
        "title": "Encryption and Data Protection",
        "content": """
NeoBank ENCRYPTION AND DATA PROTECTION:

DATA ENCRYPTION:
- All data in transit: TLS 1.3 (Transport Layer Security)
- All data at rest: AES-256 encryption
- Database encryption: Transparent Data Encryption (TDE)
- Backup encryption: AES-256 with separate key management
- Key management: AWS KMS (Key Management Service) with HSM-backed keys
- Certificate: EV SSL Certificate, 2048-bit RSA

PERSONAL DATA PROTECTION:
- Compliant with: RBI Data Localization norms, IT Act 2000, PDPB (India)
- Data stored exclusively on servers located in India
- No personal data sold or shared with third parties for marketing
- Data anonymization for analytics: All PII removed before analysis
- GDPR-equivalent rights: Right to access, correct, delete your data

PAYMENT SECURITY:
- PCI-DSS Level 1 certified (highest level of payment security)
- Card data: Never stored on NeoBank servers (tokenization via Visa/Mastercard)
- CVV: Never stored anywhere
- 3D Secure (3DS2) for all online card transactions
- Dynamic CVV for Premium debit cards

API SECURITY:
- OAuth 2.0 + JWT tokens for API authentication
- API rate limiting: 100 requests/minute per user
- IP whitelisting for business API clients
- All API calls logged and monitored

PRIVACY POLICY HIGHLIGHTS:
- Data retained for 7 years post account closure (RBI requirement)
- Right to download your data: Available via app (Data Export feature)
- Consent management: Granular controls for marketing communications
- Third-party sharing: Only with RBI-regulated entities and as required by law
        """,
        "tags": ["encryption", "tls", "aes", "data protection", "pci-dss", "privacy", "gdpr"]
    },

    {
        "id": "security_fraud_001",
        "category": "security",
        "title": "Fraud Protection",
        "content": """
NeoBank FRAUD PROTECTION SYSTEM:

AI-POWERED FRAUD DETECTION:
- Real-time ML model analyzes every transaction
- Behavioral biometrics: Typing pattern, device usage, location
- Anomaly detection: Flags unusual patterns (odd hours, new location, large amounts)
- Device fingerprinting: Detects account access from unfamiliar devices
- Velocity checks: Multiple rapid transactions trigger review
- Network analysis: Detects if payee is linked to known fraud networks

REAL-TIME ALERTS:
- Instant push notification for every transaction
- SMS alert for transactions above ₹500
- Email summary for daily transactions above ₹10,000
- Immediate alert for any international transaction
- Alert for any new payee addition

FRAUD RESPONSE PROTOCOL:
1. Suspicious transaction flagged → Customer gets instant alert
2. Customer can mark transaction as fraud in-app (one tap)
3. Card/account temporarily frozen instantly
4. Fraud team contacted within 15 minutes
5. Investigation completed within 7 working days
6. Provisional credit (for amounts above ₹10,000) within 10 days if prima facie fraud

ZERO LIABILITY POLICY:
You are not liable for unauthorized transactions if:
- You report within 3 working days: Zero liability
- Report within 4-7 days: Liability capped at ₹5,000 or transaction amount, whichever lower
- Report after 7 days: Liability as per bank policy (RBI circular RBI/2017-18/15)

PHISHING PROTECTION:
- NeoBank will NEVER ask for OTP, MPIN, or passwords via phone/email/SMS
- Official communication only from: @neobank.com email domain
- Verify any suspicious call by hanging up and calling 1800-NEOBANK

CARD FRAUD PROTECTION:
- Chip + PIN technology on all physical cards
- Zero foreign transaction liability if card reported stolen before transaction
- Contactless limit: ₹5,000 per tap (no PIN needed)
- Contactless daily limit: ₹15,000 (after which PIN required)
        """,
        "tags": ["fraud", "protection", "ml", "ai", "zero liability", "phishing", "card fraud"]
    },

    {
        "id": "security_features_001",
        "category": "security",
        "title": "Account Security Features",
        "content": """
NeoBank ACCOUNT SECURITY FEATURES:

IN-APP CONTROLS:
1. Transaction lock: Pause all debit transactions instantly
2. Card controls: Disable ATM/online/contactless/international separately
3. Spending limits: Set custom daily/weekly limits per category
4. Merchant blocking: Block specific merchant categories (gaming, adult, etc.)
5. Geographic restrictions: Allow transactions only in selected countries
6. Time-based restrictions: Block transactions outside business hours
7. Cooling period: New payees require 24-hour waiting period (configurable)

ACCOUNT MONITORING:
- View all active sessions (mobile, web, API)
- Remote logout from any device
- Transaction history with merchant details, IP address
- Login history with timestamp, device, location
- Failed login attempt history

DEVICE MANAGEMENT:
- Register up to 3 trusted devices
- Unrecognized device login requires video selfie + OTP
- Device deregistration possible anytime from app
- Stolen device: Remotely wipe NeoBank app data via web portal

ACCOUNT FREEZE/UNFREEZE:
- Self-service freeze: Instant via app or web
- Temporary freeze: 1-30 days (auto-unfreeze)
- Permanent freeze: Requires customer care contact for unfreeze
- Frozen account: No debits, all credits accepted

NOMINEE AND SUCCESSION:
- Add up to 2 nominees per account
- Nomination percentage split available
- Joint account options: Either/Survivor, Former/Survivor, Joint
- Digital will registration available through partner service (Khata)
        """,
        "tags": ["security features", "card controls", "freeze", "nominee", "device management"]
    },

    # ── INSURANCE ──────────────────────────────────────────────────
    {
        "id": "insurance_fdic_001",
        "category": "insurance",
        "title": "DICGC Insurance (India equivalent of FDIC)",
        "content": """
NeoBank DEPOSIT INSURANCE:

DICGC COVERAGE (Deposit Insurance and Credit Guarantee Corporation):
NeoBank is a member of DICGC, a wholly owned subsidiary of the Reserve Bank of India.

COVERAGE AMOUNT:
- Maximum insured: ₹5,00,000 per depositor per bank
- Coverage includes: Principal + accrued interest
- This limit covers ALL deposits combined at NeoBank:
  savings + current + fixed deposits + recurring deposits

WHAT IS COVERED:
✓ Savings account balances
✓ Current/checking account balances
✓ Fixed deposit principal + interest
✓ Recurring deposit amounts
✓ Staff accounts
✓ NRI accounts (NRO/NRE)

WHAT IS NOT COVERED:
✗ Deposits held by state/central government
✗ Deposits placed by other banks
✗ Amounts due on account of deposits outside India

HOW DICGC WORKS:
- Premium paid by NeoBank: 0.12% of total deposits annually (not charged to customers)
- In case of bank failure, DICGC pays within 90 days
- No action needed from depositor — automatic protection

PROTECTING DEPOSITS ABOVE ₹5 LAKH:
If you have more than ₹5 lakh to deposit:
1. Spread across multiple banks (each gets ₹5 lakh cover)
2. Joint accounts: Both individual and joint accounts get separate ₹5 lakh coverage
3. Consider RBI Sovereign Gold Bonds or Government Securities for amounts above insurance limit

NOTE: This is analogous to FDIC insurance in the USA ($250,000 coverage).
DICGC provides equivalent protection for Indian depositors.
For complete details: www.dicgc.org.in
        """,
        "tags": ["dicgc", "fdic", "insurance", "deposit protection", "rbi", "coverage"]
    },

    # ── HOW TO OPEN ────────────────────────────────────────────────
    {
        "id": "onboarding_001",
        "category": "onboarding",
        "title": "How to Open a NeoBank Account",
        "content": """
HOW TO OPEN A NEOBANK ACCOUNT:

STEP-BY-STEP PROCESS (takes 5-10 minutes):

STEP 1: DOWNLOAD APP / VISIT WEBSITE
- Download NeoBank app from Google Play Store or Apple App Store
- OR visit app.neobank.com on web browser
- Click "Open Account" / "Sign Up"

STEP 2: ENTER BASIC DETAILS
- Full name (as per PAN/Aadhaar)
- Mobile number (linked to Aadhaar)
- Email address
- Date of birth

STEP 3: OTP VERIFICATION
- OTP sent to mobile (linked to Aadhaar)
- Enter 6-digit OTP within 10 minutes
- Second OTP sent to email for confirmation

STEP 4: e-KYC via AADHAAR
- Enter 12-digit Aadhaar number
- OTP sent to Aadhaar-linked mobile by UIDAI
- Demographic data (name, DOB, address) fetched automatically
- FULL Aadhaar number masked after verification — NeoBank only stores last 4 digits

STEP 5: PAN VERIFICATION
- Enter PAN card number
- Verified automatically against Income Tax database
- NSDL/UTI verification completed in seconds

STEP 6: VIDEO KYC (Required for full account)
- Schedule video call (available 9 AM - 9 PM, 7 days a week)
- Takes 3-5 minutes
- NeoBank agent verifies you via live video
- Show original PAN and Aadhaar during video call
- Video recorded and stored securely

STEP 7: ACCOUNT ACTIVATION
- Account number generated instantly after Video KYC
- Virtual debit card issued immediately
- IFSC code: NEOB0001234
- Physical debit card dispatched within 5-7 working days

INITIAL DEPOSIT:
- Zero Balance account: No initial deposit required
- Classic Savings: ₹1,000 recommended
- Premium Account: ₹5,00,000 initial deposit for eligibility

DOCUMENTS SUMMARY:
Mandatory: PAN Card, Aadhaar (for e-KYC)
Optional: Passport (for NRI accounts), Form 60 (if no PAN)
        """,
        "tags": ["open account", "kyc", "aadhaar", "pan", "video kyc", "onboarding", "sign up"]
    },

    # ── CONTACT AND SUPPORT ────────────────────────────────────────
    {
        "id": "contact_001",
        "category": "contact",
        "title": "Contact Methods and Support",
        "content": """
NEOBANK CONTACT AND SUPPORT:

CUSTOMER CARE:
- Toll-free: 1800-NEOBANK (1800-636-2265) — Available 24×7×365
- Premium priority line: 1800-NEO-PREM (1800-636-7736) — 30-second answer guarantee
- International (chargeable): +91-22-6123-4567
- Languages supported: English, Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, Gujarati

IN-APP SUPPORT:
- Live chat: Available in app, 24×7, average response 2 minutes
- AI chatbot: Instant answers for common queries
- Call back request: Schedule a call within 15 minutes to 24 hours
- Screen sharing: Agent can view your app (with permission) for complex issues

EMAIL SUPPORT:
- General: support@neobank.com (response within 24 hours)
- Complaints: grievance@neobank.com (response within 48 hours per RBI)
- Fraud reporting: fraud@neobank.com (response within 4 hours)
- Premium accounts: premium.support@neobank.com (response within 2 hours)

SOCIAL MEDIA:
- Twitter/X: @NeoBankIndia (monitored 9 AM - 9 PM)
- Facebook: /NeoBankIndia
- Instagram: @neobank.india
- LinkedIn: NeoBank India

BRANCH SUPPORT:
NeoBank is primarily digital, but we have partner touch points:
- 200+ Video Banking Kiosks across 50 major cities
- Banking correspondent locations: 5,000+ across India (via partner CSPs)
- NeoBank Lounges (premium customers): Mumbai, Delhi, Bangalore, Chennai, Hyderabad
- All locations: neobank.com/locate

ESCALATION MATRIX:
Level 1: Customer care executive (first point of contact)
Level 2: Senior executive (if not resolved in 24 hours)
Level 3: Grievance officer (if not resolved in 3 working days)
Level 4: Banking Ombudsman (RBI) — if not resolved in 30 days
RBI Ombudsman: https://cms.rbi.org.in
        """,
        "tags": ["contact", "customer care", "support", "phone", "email", "chat", "branch", "escalation"]
    },

    {
        "id": "contact_digital_001",
        "category": "contact",
        "title": "Digital Support Channels",
        "content": """
NEOBANK DIGITAL SUPPORT CHANNELS:

MOBILE APP SUPPORT:
- NeoBank App v5.x (iOS 14+ / Android 8+)
- In-app help center: 500+ articles, video tutorials
- AI Assistant: Available 24×7, handles 80% of queries instantly
- Human escalation: From AI to human in <2 minutes
- Push notifications: Transactional, offers, security alerts
- Accessibility: Screen reader compatible, high contrast mode

WEB BANKING (app.neobank.com):
- Full-featured web banking on desktop/laptop
- Compatible: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Live chat widget: Bottom right corner, 24×7
- Secure messaging: Send documents securely through web portal
- Callback request: Schedule callback from web interface

WHATSAPP BANKING:
- Number: +91-90000-NEOBANK
- Features: Balance check, mini statement, transaction alerts
- Fully encrypted end-to-end
- Available 24×7 for automated services, 9 AM - 9 PM for human agents

SMS BANKING:
- BAL to 56161 for balance
- MINI to 56161 for last 5 transactions
- BLOCK to 56161 to block debit card instantly
- Works without internet — useful in emergencies

IVR SYSTEM (Phone Banking):
- Account balance: Press 1
- Last 5 transactions: Press 2
- Block card: Press 3
- Speak to executive: Press 0
- Available 24×7 for automated options

SELF-SERVICE KIOSKS:
- Located in 200 cities
- Services: Cash deposit, cheque deposit, account statement, card replacement request
- Available: 8 AM - 10 PM daily
        """,
        "tags": ["digital", "app", "web banking", "whatsapp", "sms", "ivr", "self service"]
    },

    # ── SPECIAL REQUESTS ───────────────────────────────────────────
    {
        "id": "special_requests_001",
        "category": "special_requests",
        "title": "Special Requests and Services",
        "content": """
NEOBANK SPECIAL REQUESTS:

ACCOUNT SERVICES:
- Name change (marriage/legal): Requires court order/marriage certificate, 5-7 days
- Address update: Instant via app with Aadhaar e-KYC
- Email/mobile update: Requires OTP on both old and new contact, 24 hours
- Nominee addition/change: Instant via app
- KYC update: Video KYC re-verification, 2-3 days

TRANSACTION SERVICES:
- Recall/reversal of wrong NEFT: Submit within 2 hours, 3-5 day resolution
- Stop payment on cheque: ₹100, instant via app
- Post-dated cheque management: Up to 90 days advance, ₹50 per cheque
- Bulk salary upload: Available for businesses, next-day processing

LOAN AND CREDIT:
- Pre-approved personal loan: Check eligibility in app (instant decision)
- Overdraft request on checking account: 2-3 business days
- Credit limit enhancement on overdraft: Annual review or on-demand
- Loan statement for IT filing: Free, instant download

ACCOUNT OPERATIONS:
- Account closure: Must clear all dues, close via app or customer care
- Dormant account reactivation: ₹100 fee, ID proof required
- Account freeze/unfreeze: Instant self-service via app
- Power of attorney: Requires notarized POA, 5-7 days processing
- Estate/succession: Nomination claim processed within 15 days

CERTIFICATES AND DOCUMENTS:
- Balance certificate: ₹50, instant digital, ₹200 physical with bank seal
- Interest certificate (for IT purposes): FREE, instant download (available Jan-Mar)
- No-dues certificate: ₹100, 2-3 days
- Account statement (custom date range): FREE via app
- Loan NOC: ₹200, 5-7 days after full repayment
- CIBIL dispute resolution: FREE, 30 days

PREMIUM-ONLY SERVICES:
- Portfolio review with wealth manager: Monthly, by appointment
- Tax planning advisory: Annual, included in premium
- Estate planning consultation: Available through partner firm
- Concierge services: Travel, dining, entertainment booking
        """,
        "tags": ["special requests", "name change", "address update", "recall", "certificates", "closure"]
    },

    # ── LOST/STOLEN / EMERGENCY ────────────────────────────────────
    {
        "id": "emergency_001",
        "category": "emergency",
        "title": "Lost or Stolen Card / Account",
        "content": """
LOST OR STOLEN CARD — IMMEDIATE ACTIONS:

STEP 1 — BLOCK IMMEDIATELY (any of these methods):
a) App: Home → Cards → Block Card (INSTANT, available 24×7)
b) SMS: BLOCK to 56161 (INSTANT, no internet needed)
c) IVR: 1800-NEOBANK → Press 3 (INSTANT)
d) WhatsApp: Send "BLOCK CARD" to +91-90000-NEOBANK

Once blocked, card cannot be used for ANY transaction.
Existing UPI/NACH mandates linked to account continue working.

STEP 2 — REPORT TO BANK:
- Call 1800-NEOBANK and report card lost/stolen
- File a police FIR (especially for stolen card)
- Share FIR copy with bank for zero liability claim

STEP 3 — REPLACEMENT CARD:
- Request replacement via app → Cards → Request Replacement
- Standard delivery: 5-7 working days, ₹200 fee
- Express delivery: 48 hours, ₹350 fee
- Instant virtual card: Issued immediately (for online use) FREE
- New card has different card number — update saved payments

UNAUTHORIZED TRANSACTIONS:
- Dispute window: 60 days from statement date (RBI mandate)
- Emergency credit: Up to ₹10,000 credited within 24 hours while investigation ongoing (for verified customers)
- Full reversal: Within 7-10 working days if fraud confirmed

LOST PHONE WITH NEOBANK APP:
1. Login to app.neobank.com from another device
2. Go to Security → Active Devices → Remote Logout
3. Your app data on lost phone is wiped remotely
4. Change MPIN immediately via web portal
5. Call 1800-NEOBANK to report and block if suspicious activity seen

PASSWORD RESET / MPIN RESET:
- App login page → "Forgot MPIN"
- Verify via: Registered mobile OTP + Aadhaar OTP (or biometric if registered)
- New MPIN set within 2 minutes — no branch visit needed
- Web banking password: Reset via email link, requires additional OTP verification
- If mobile number also lost: Visit nearest NeoBank kiosk with Aadhaar + PAN
        """,
        "tags": ["lost card", "stolen", "block card", "emergency", "password reset", "mpin reset", "unauthorized"]
    },

    # ── BANKING POLICIES ───────────────────────────────────────────
    {
        "id": "policy_001",
        "category": "policy",
        "title": "Bank Policies Overview",
        "content": """
NEOBANK KEY POLICIES:

FAIR PRACTICES CODE:
NeoBank follows RBI Fair Practices Code:
- Transparent pricing: All fees listed on website, no hidden charges
- Clear communication: All terms in simple language
- No mis-selling: Products recommended only if suitable for customer
- Customer grievance: Resolved within 30 days per RBI guidelines

KYC POLICY:
- Full KYC: Required for accounts above ₹50,000 balance or ₹1,00,000 annual credits
- Small KYC (Self-declaration): For accounts up to ₹50,000 with limited functionality
- Re-KYC: Every 10 years for low risk, 8 years for medium risk, 2 years for high risk
- KYC update refusal: Bank may restrict account if KYC not updated when asked

ANTI-MONEY LAUNDERING (AML):
- Transactions above ₹10 lakh in cash: Reported to FIU (Financial Intelligence Unit)
- Suspicious transactions: Reported via STR to FIU within 7 days
- High-risk customers: Enhanced due diligence applied
- PEPs (Politically Exposed Persons): Special monitoring requirements

INTEREST RATE POLICY:
- Rates reviewed quarterly by Asset-Liability Committee (ALCO)
- Changes notified 30 days in advance for fixed deposits
- Savings account rate changes: 7 days notice
- All rate changes published on website and communicated via app

DORMANCY POLICY:
- Account dormant after: 24 months of no customer-initiated transactions
- Pre-dormancy notice: SMS + email 30 days before
- Dormancy activation: Self-service via app or branch with ID proof, ₹100 fee
- Unclaimed deposits: Transferred to RBI DEAF (Depositor Education and Awareness Fund)
  after 10 years of inoperative status

NOMINATION POLICY:
- Strongly recommended for all accounts
- Up to 2 nominees, with percentage split
- Nominee claim: Submit death certificate + nominee ID + claim form
- Processing: 15 working days from complete documents
- Dispute in nominee claims: Referred to civil court per Indian Succession Act
        """,
        "tags": ["policy", "kyc", "aml", "fair practices", "dormancy", "nomination", "rbi"]
    },

    # ── HOW TO USE NEOBANK ─────────────────────────────────────────
    {
        "id": "howto_deposit_001",
        "category": "howto",
        "title": "How to Deposit Money",
        "content": """
HOW TO DEPOSIT MONEY IN NEOBANK:

METHOD 1: NEOBANK APP (Instant)
1. Open NeoBank app → Login
2. Tap "Deposit" on home screen or bottom navigation
3. Enter amount and optional note/description
4. Confirm with MPIN or biometric
5. Money credited instantly to your account

METHOD 2: UPI (Instant)
- Share your NeoBank UPI ID: yourname@neobank
- Anyone can send money to this UPI ID from any UPI app
- Credited within seconds, available 24×7

METHOD 3: IMPS/NEFT/RTGS (from another bank)
- Account number: Your NeoBank account number
- IFSC: NEOB0001234
- Use these details to transfer from any other bank
- IMPS: Instant, 24×7
- NEFT: Near real-time (RBI NEFT available 24×7 since Dec 2019)
- RTGS: For amounts above ₹2 lakh, real-time during bank hours

METHOD 4: CHEQUE DEPOSIT
- Via NeoBank app: Take photo of cheque (CTS clearing)
- Via kiosk: Insert cheque in self-service kiosk
- Clearing time: 1-2 working days

METHOD 5: CASH DEPOSIT
- At banking correspondents / CSP locations
- At partner bank branches (HDFC, ICICI white-label counters)
- Cash deposit limit: ₹49,999 without PAN (above requires PAN)

DEPOSIT CONFIRMATION:
- Instant push notification on app
- SMS (if enabled)
- Balance reflected immediately
        """,
        "tags": ["deposit", "how to", "upi", "neft", "cash deposit", "imps"]
    },

    {
        "id": "howto_transfer_001",
        "category": "howto",
        "title": "How to Transfer Money",
        "content": """
HOW TO TRANSFER MONEY FROM NEOBANK:

NEOBANK TO NEOBANK (Internal Transfer):
1. App → Transfer → NeoBank Transfer
2. Enter recipient's NeoBank account number OR mobile number OR UPI ID
3. Enter amount and note
4. Confirm with MPIN
5. Instant credit — 24×7, no charges

UPI TRANSFER:
1. App → UPI → Send Money
2. Enter UPI ID / scan QR code / select from contacts
3. Enter amount, add note
4. Authenticate with UPI PIN
5. Instant credit to any UPI-enabled bank account

IMPS (to other banks):
1. App → Transfer → IMPS
2. Add payee: Account number + IFSC (first-time payee needs 24h cooling period)
3. Enter amount (up to ₹5 lakh per transaction)
4. Confirm with MPIN + OTP (for new payee)
5. Instant credit (24×7)

NEFT:
1. App → Transfer → NEFT
2. Select payee from list or add new
3. Enter amount
4. Schedule now or future date
5. Near real-time credit

RTGS (above ₹2 lakh):
1. App → Transfer → RTGS
2. Select payee
3. Enter amount (minimum ₹2 lakh)
4. Real-time credit during RBI RTGS hours

INTERNATIONAL WIRE (SWIFT):
1. App → Transfer → International
2. Enter recipient bank details: SWIFT code, IBAN/account, bank address
3. Enter amount and purpose of remittance
4. Complete LRS declaration if applicable
5. 2-5 business days

ADDING A NEW PAYEE:
- First-time payee: 24-hour cooling period (security measure)
- Can override for trusted payees with video verification
- Payee saved automatically after first successful transfer
        """,
        "tags": ["transfer", "upi", "imps", "neft", "rtgs", "swift", "payee", "how to"]
    },
]


def get_all_documents():
    """Return all knowledge base documents."""
    return DOCUMENTS


def get_documents_by_category(category: str):
    """Filter documents by category."""
    return [d for d in DOCUMENTS if d["category"] == category]


def get_document_by_id(doc_id: str):
    """Get a specific document by ID."""
    for d in DOCUMENTS:
        if d["id"] == doc_id:
            return d
    return None


def get_all_categories():
    """Return unique list of categories."""
    return list(set(d["category"] for d in DOCUMENTS))


def get_full_text_for_category(category: str) -> str:
    """Return combined text of all documents in a category."""
    docs = get_documents_by_category(category)
    return "\n\n".join(f"## {d['title']}\n{d['content']}" for d in docs)
