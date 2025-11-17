"""
Generate PDF versions of supplier statements for OCR testing
Replicates realistic statement formats based on real-world examples
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
import json
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

# Try to import dotenv for loading environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not available, using system environment variables")

# Try to import OpenAI for realistic data generation
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI not available, using fallback data generation")


class RealisticDataGenerator:
    """Generate realistic statement data using OpenAI or fallback methods"""

    def __init__(self, use_openai=True):
        self.use_openai = use_openai and OPENAI_AVAILABLE
        if self.use_openai:
            try:
                self.client = OpenAI()
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}")
                self.use_openai = False

        # Fallback company data
        self.companies = [
            {"name": "Northern Foods Supply Co.", "address": "1234 Industrial Blvd\nToronto ON M5V 2T6", "phone": "(416) 555-0123", "email": "ar@northernfoods.ca"},
            {"name": "Pacific Seafood Distributors", "address": "890 Harbor Drive\nVancouver BC V6B 4N9", "phone": "(604) 555-0456", "email": "accounts@pacificseafood.ca"},
            {"name": "Prairie Grain Merchants Ltd.", "address": "456 Wheat Avenue\nWinnipeg MB R3C 0V8", "phone": "(204) 555-0789", "email": "billing@prairiegrain.ca"},
            {"name": "Atlantic Dairy Products Inc.", "address": "321 Coastal Road\nHalifax NS B3J 1P3", "phone": "(902) 555-0321", "email": "finance@atlanticdairy.ca"},
            {"name": "Mountain Fresh Produce Ltd.", "address": "567 Valley Road\nCalgary AB T2P 1J9", "phone": "(403) 555-0654", "email": "receivables@mountainfresh.ca"},
            {"name": "Great Lakes Equipment Co.", "address": "789 Lakeshore Blvd\nHamilton ON L8P 4X1", "phone": "(905) 555-0987", "email": "ar@greatlakesequip.ca"},
            {"name": "Quebec Artisan Foods", "address": "234 Rue Saint-Laurent\nMontreal QC H2Y 2Y3", "phone": "(514) 555-0234", "email": "comptes@quebecartisan.ca"},
            {"name": "Western Machinery Parts", "address": "678 Industrial Park Way\nEdmonton AB T5J 3N8", "phone": "(780) 555-0567", "email": "billing@westernmachinery.ca"},
            {"name": "Maritime Packaging Solutions", "address": "123 Shipyard Lane\nSaint John NB E2L 4L5", "phone": "(506) 555-0890", "email": "accounts@maritimepack.ca"},
            {"name": "Central Canada Chemicals", "address": "345 Research Drive\nOttawa ON K1N 6N5", "phone": "(613) 555-0432", "email": "finance@centralchem.ca"},
        ]

        self.customers = [
            {"name": "SOBEYS INC.", "address": "115 King Street\nStellarton NS B0K 1S0", "account": "SOB001"},
            {"name": "METRO INC.", "address": "11011 Maurice-Duplessis Blvd\nMontreal QC H1C 1V6", "account": "MET002"},
            {"name": "LOBLAWS COMPANIES", "address": "1 President's Choice Circle\nBrampton ON L6Y 5S5", "account": "LOB003"},
            {"name": "COSTCO WHOLESALE", "address": "415 West Hunt Club Road\nOttawa ON K2E 1C5", "account": "COS004"},
            {"name": "WALMART CANADA", "address": "1940 Argentia Road\nMississauga ON L5N 1P9", "account": "WAL005"},
        ]

        self.transaction_types = {
            "invoice": {"prefix": "INV", "is_debit": True},
            "credit_note": {"prefix": "CN", "is_debit": False},
            "payment": {"prefix": "PY", "is_debit": False},
            "debit_note": {"prefix": "DN", "is_debit": True},
            "adjustment": {"prefix": "ADJ", "is_debit": None},
        }

        self.descriptions = [
            "Product delivery", "Service charges", "Shipping and handling",
            "Monthly supplies", "Equipment rental", "Maintenance fees",
            "Raw materials", "Packaging supplies", "Quality inspection",
            "Storage fees", "Transportation", "Processing charges",
            "Damage claim", "Returned goods", "Price adjustment",
            "Volume discount", "Early payment discount", "Late fee waiver",
        ]

    def generate_company(self):
        """Generate realistic company data"""
        if self.use_openai:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{
                        "role": "user",
                        "content": """Generate a realistic Canadian business for a supplier statement. Return JSON with:
                        {
                            "name": "Company Name Ltd.",
                            "address": "Street Address\\nCity Province PostalCode",
                            "phone": "(XXX) XXX-XXXX",
                            "email": "accounts@domain.ca",
                            "website": "www.domain.ca"
                        }
                        Make it sound like a real food/manufacturing supplier."""
                    }],
                    max_tokens=200,
                    temperature=0.9
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"OpenAI error: {e}")

        return random.choice(self.companies)

    def generate_customer(self):
        """Generate realistic customer data"""
        return random.choice(self.customers)

    def generate_transactions(self, num_transactions=10, opening_balance=0):
        """Generate realistic transaction flow"""
        transactions = []
        current_balance = Decimal(str(opening_balance))
        base_date = datetime.now() - timedelta(days=90)

        for i in range(num_transactions):
            trans_date = base_date + timedelta(days=random.randint(1, 90))
            trans_type = random.choices(
                ["invoice", "credit_note", "payment", "debit_note"],
                weights=[0.5, 0.15, 0.25, 0.1]
            )[0]

            type_info = self.transaction_types[trans_type]
            reference = f"{type_info['prefix']}{random.randint(10000, 99999)}"

            # Generate realistic amounts
            if trans_type == "invoice":
                amount = Decimal(str(random.uniform(100, 25000))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                current_balance += amount
            elif trans_type == "credit_note":
                max_credit = min(float(current_balance) * 0.3, 5000) if current_balance > 0 else 500
                amount = Decimal(str(random.uniform(10, max(50, max_credit)))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                current_balance -= amount
            elif trans_type == "payment":
                if current_balance > 0:
                    amount = Decimal(str(random.uniform(float(current_balance) * 0.1, float(current_balance) * 0.8))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                else:
                    amount = Decimal(str(random.uniform(100, 5000))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                current_balance -= amount
            else:  # debit_note
                amount = Decimal(str(random.uniform(10, 500))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                current_balance += amount

            transactions.append({
                "date": trans_date.strftime("%d/%m/%Y"),
                "date_obj": trans_date,
                "type": trans_type,
                "reference": reference,
                "description": random.choice(self.descriptions),
                "amount": float(amount),
                "balance_after": float(current_balance),
                "is_credit": not type_info['is_debit'] if type_info['is_debit'] is not None else random.choice([True, False]),
                "is_debit": type_info['is_debit'] if type_info['is_debit'] is not None else random.choice([True, False]),
                "po_number": f"PO{random.randint(100000, 999999)}" if random.random() > 0.3 else "",
                "due_date": (trans_date + timedelta(days=30)).strftime("%d/%m/%Y"),
            })

        # Sort by date
        transactions.sort(key=lambda x: x["date_obj"])

        # Recalculate balances after sorting
        current_balance = Decimal(str(opening_balance))
        for trans in transactions:
            if trans["is_debit"]:
                current_balance += Decimal(str(trans["amount"]))
            else:
                current_balance -= Decimal(str(trans["amount"]))
            trans["balance_after"] = float(current_balance)

        return transactions, float(current_balance)

    def calculate_aging(self, transactions):
        """Calculate aging buckets based on transactions"""
        today = datetime.now()
        aging = {
            "current": 0,
            "days_1_30": 0,
            "days_31_60": 0,
            "days_61_90": 0,
            "days_90_plus": 0,
        }

        for trans in transactions:
            if trans["is_debit"]:
                days_old = (today - trans["date_obj"]).days
                if days_old <= 0:
                    aging["current"] += trans["amount"]
                elif days_old <= 30:
                    aging["days_1_30"] += trans["amount"]
                elif days_old <= 60:
                    aging["days_31_60"] += trans["amount"]
                elif days_old <= 90:
                    aging["days_61_90"] += trans["amount"]
                else:
                    aging["days_90_plus"] += trans["amount"]

        return aging


class StatementPDFGenerator:
    """Generate realistic PDF supplier statements in multiple formats"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.data_generator = RealisticDataGenerator()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6
        ))

        self.styles.add(ParagraphStyle(
            name='CompanyNameLarge',
            parent=self.styles['Heading1'],
            fontSize=20,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=2
        ))

        self.styles.add(ParagraphStyle(
            name='StatementTitle',
            parent=self.styles['Heading2'],
            fontSize=24,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#333333'),
            spaceAfter=12
        ))

        self.styles.add(ParagraphStyle(
            name='StatementTitleGray',
            parent=self.styles['Heading2'],
            fontSize=20,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=12
        ))

        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT
        ))

        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666')
        ))

        self.styles.add(ParagraphStyle(
            name='BoldRed',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#CC0000')
        ))

    def generate_statement_style1(self, output_path: str, statement_data: dict = None):
        """
        Sheldon Creek Dairy Style - Clean professional format
        Features: Logo top-right, aging at bottom, simple transaction list
        """
        if statement_data is None:
            statement_data = self._generate_statement_data()

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        story = []

        # Company header (top-left)
        company = statement_data["company"]
        story.append(Paragraph(f"<b>{company['name']}</b>", self.styles['Normal']))
        for line in company['address'].split('\n'):
            story.append(Paragraph(line, self.styles['Normal']))
        story.append(Paragraph(company.get('phone', ''), self.styles['Normal']))
        story.append(Paragraph(company.get('email', ''), self.styles['Normal']))
        if company.get('website'):
            story.append(Paragraph(company['website'], self.styles['Normal']))

        story.append(Spacer(1, 0.3*inch))

        # Statement title
        story.append(Paragraph("Statement", self.styles['StatementTitle']))
        story.append(Spacer(1, 0.2*inch))

        # Two-column layout for TO and Statement info
        customer = statement_data["customer"]
        to_info = f"""<b>TO</b><br/>
        {customer['name']}<br/>
        {customer['address'].replace(chr(10), '<br/>')}"""

        statement_info = f"""<b>STATEMENT NO.</b> {statement_data['statement_number']}<br/>
        <b>DATE</b> {statement_data['statement_date']}<br/>
        <b>TOTAL DUE</b> $ {statement_data['total_due']:,.2f}<br/>
        <b>ENCLOSED</b>"""

        info_table = Table([
            [Paragraph(to_info, self.styles['Normal']), Paragraph(statement_info, self.styles['RightAlign'])]
        ], colWidths=[3.5*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(info_table)

        story.append(Spacer(1, 0.3*inch))

        # Transaction table
        table_data = [['DATE', 'DESCRIPTION', 'AMOUNT', 'OPEN AMOUNT']]
        for trans in statement_data['transactions']:
            amount = trans['amount'] if trans['is_debit'] else -trans['amount']
            table_data.append([
                trans['date'],
                trans['description'],
                f"{amount:,.2f}",
                f"{trans['balance_after']:,.2f}"
            ])

        trans_table = Table(table_data, colWidths=[1.2*inch, 3*inch, 1.3*inch, 1.3*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(trans_table)

        story.append(Spacer(1, 1*inch))

        # Aging buckets at bottom
        aging = statement_data['aging']
        aging_data = [
            ['Current\nDue', '1-30 Days\nPast Due', '31-60 Days\nPast Due', '61-90 Days\nPast Due', '90+ Days\nPast Due', '', 'Amount\nDue'],
            [f"{aging['current']:,.2f}", f"{aging['days_1_30']:,.2f}", f"{aging['days_31_60']:,.2f}",
             f"{aging['days_61_90']:,.2f}", f"{aging['days_90_plus']:,.2f}", '', f"$ {statement_data['total_due']:,.2f}"]
        ]

        aging_table = Table(aging_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 0.5*inch, 1.3*inch])
        aging_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTNAME', (-1, 1), (-1, 1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (-1, 1), (-1, 1), colors.HexColor('#CC0000')),
        ]))
        story.append(aging_table)

        story.append(Spacer(1, 0.2*inch))

        # Thank you message
        story.append(Paragraph("<b>THANK YOU FOR YOUR ORDER!</b>", ParagraphStyle('Center', alignment=TA_CENTER, fontSize=10)))
        story.append(Paragraph(f"Please ensure payments are made payable to:<br/><b>{company['name'].upper()}</b>",
                              ParagraphStyle('Center', alignment=TA_CENTER, fontSize=9)))

        doc.build(story)

    def generate_statement_style2(self, output_path: str, statement_data: dict = None):
        """
        Cultures Gen V Style - Corporate multi-page format
        Features: Document types, green header rows, credit limit info
        """
        if statement_data is None:
            statement_data = self._generate_statement_data(num_transactions=15)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        story = []

        company = statement_data["company"]
        customer = statement_data["customer"]

        # Header with company name and STATEMENT banner
        header_table = Table([
            [Paragraph(f"<b>{company['name']}</b>", self.styles['CompanyName']),
             Paragraph("<b>STATEMENT</b>", self.styles['StatementTitleGray'])]
        ], colWidths=[3.5*inch, 3.5*inch])
        story.append(header_table)

        # Company address
        for line in company['address'].split('\n'):
            story.append(Paragraph(line, self.styles['Normal']))

        story.append(Spacer(1, 0.2*inch))

        # Customer number box (right aligned)
        info_box_data = [
            ['CUSTOMER NO.:', customer['account']],
            ['PAGE:', '1'],
            ['DATE:', statement_data['statement_date']]
        ]
        info_box = Table(info_box_data, colWidths=[1.5*inch, 1.5*inch])
        info_box.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))

        # Sold To and Remit To sections
        sold_to = f"<b>SOLD TO:</b><br/>{customer['name']}<br/>{customer['address'].replace(chr(10), '<br/>')}"
        remit_to = f"<b>REMIT TO ADDRESS:</b><br/>{company['name']}<br/>{company['address'].replace(chr(10), '<br/>')}"

        address_table = Table([
            [Paragraph(sold_to, self.styles['Normal']),
             Paragraph(remit_to, self.styles['Normal']),
             info_box]
        ], colWidths=[2.5*inch, 2.5*inch, 3*inch])
        address_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(address_table)

        story.append(Spacer(1, 0.3*inch))

        # Transaction table with green header
        table_data = [['DOCUMENT NUMBER', 'DOCUMENT DATE', 'Type', 'REFERENCE/APPLIED NUMBER', 'DUE DATE', 'AMOUNT']]

        type_map = {
            'invoice': 'IN',
            'credit_note': 'CR',
            'payment': 'PY',
            'debit_note': 'DB',
            'adjustment': 'AD'
        }

        for trans in statement_data['transactions']:
            doc_type = type_map.get(trans['type'], 'IN')
            amount = trans['amount'] if trans['is_debit'] else -trans['amount']
            table_data.append([
                trans['reference'],
                trans['date'],
                doc_type,
                trans.get('po_number', ''),
                trans['due_date'],
                f"{amount:,.2f}"
            ])

        trans_table = Table(table_data, colWidths=[1.3*inch, 1.1*inch, 0.5*inch, 1.8*inch, 1*inch, 1.1*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A7C3C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(trans_table)

        story.append(Spacer(1, 0.3*inch))

        # Legend and totals
        legend_text = """IN - Invoice    DB - Debit Note    CR - Credit Note    IT - Interest Payable
PY - Applied Receipt    ED - Earned Discount    AD - Adjustment    PI - Prepayment
UC - Unapplied Cash    RF - Refund"""
        story.append(Paragraph(legend_text.replace('\n', '<br/>'), self.styles['SmallText']))

        story.append(Spacer(1, 0.2*inch))

        # Credit info
        credit_limit = random.uniform(100000, 1000000)
        credit_available = credit_limit - statement_data['total_due']

        totals_data = [
            ['', '', 'Total:', f"{statement_data['total_due']:,.2f}"],
            ['', '', 'Credit Limit:', f"{credit_limit:,.2f}"],
            ['', '', 'Credit Available:', f"{credit_available:,.2f}"]
        ]
        totals_table = Table(totals_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (-2, 0), (-2, -1), 'Helvetica-Bold'),
        ]))
        story.append(totals_table)

        story.append(Spacer(1, 0.3*inch))

        # Aging at bottom
        aging = statement_data['aging']
        aging_data = [
            ['1 - 30 DAYS O/DUE', '31 - 60 DAYS O/DUE', '61 - 90 DAYS O/DUE', 'OVER 90 DAYS O/DUE'],
            [f"{aging['days_1_30']:,.2f}", f"{aging['days_31_60']:,.2f}", f"{aging['days_61_90']:,.2f}", f"{aging['days_90_plus']:,.2f}"]
        ]
        aging_table = Table(aging_data, colWidths=[1.7*inch, 1.7*inch, 1.7*inch, 1.7*inch])
        aging_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
        ]))
        story.append(aging_table)

        doc.build(story)

    def generate_statement_style3(self, output_path: str, statement_data: dict = None):
        """
        Comeau's Sea Foods Style - Bold branding with debit/credit columns
        Features: Logo prominent, running balance, interest warning
        """
        if statement_data is None:
            statement_data = self._generate_statement_data()

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        story = []

        company = statement_data["company"]
        customer = statement_data["customer"]

        # Header with company name prominently
        story.append(Paragraph(f"<font size='22' color='#0066CC'><b>{company['name']}</b></font>", self.styles['Normal']))
        for line in company['address'].split('\n'):
            story.append(Paragraph(line, self.styles['Normal']))
        story.append(Paragraph(f"Tel: {company.get('phone', '')} Fax: {company.get('phone', '').replace('555', '556')}", self.styles['Normal']))

        story.append(Spacer(1, 0.1*inch))

        # STATEMENT title centered
        story.append(Paragraph("<font size='18' color='#0066CC'><b>STATEMENT</b></font>",
                              ParagraphStyle('CenterBlue', alignment=TA_CENTER, fontSize=18)))

        story.append(Spacer(1, 0.2*inch))

        # Customer and statement info side by side
        left_info = f"""<b>{customer['name']}</b><br/>
        {customer['address'].replace(chr(10), '<br/>')}"""

        right_info = f"""<b>Cust Name:</b> {customer['name']}<br/>
        <b>Statement Date:</b> {statement_data['statement_date']}<br/>
        <b>Account #:</b> {customer['account']}"""

        info_table = Table([
            [Paragraph(left_info, self.styles['Normal']), Paragraph(right_info, self.styles['Normal'])]
        ], colWidths=[3.5*inch, 3.5*inch])
        story.append(info_table)

        story.append(Spacer(1, 0.3*inch))

        # Transaction table with Debit/Credit columns
        table_data = [['Invoice', 'Invoice Date', 'Debit', 'Credit', 'Balance']]

        running_balance = Decimal('0')
        for trans in statement_data['transactions']:
            debit_str = ""
            credit_str = ""

            if trans['is_debit']:
                debit_str = f"{trans['amount']:,.2f}"
                running_balance += Decimal(str(trans['amount']))
            else:
                credit_str = f"{trans['amount']:,.2f}"
                running_balance -= Decimal(str(trans['amount']))

            table_data.append([
                trans['reference'],
                trans['date'],
                debit_str,
                credit_str,
                f"{float(running_balance):,.2f}"
            ])

        trans_table = Table(table_data, colWidths=[1.4*inch, 1.2*inch, 1.3*inch, 1.3*inch, 1.6*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8E8E8')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(trans_table)

        story.append(Spacer(1, 0.5*inch))

        # Aging summary
        aging = statement_data['aging']
        aging_header = ['Balance Due', '0 - 30 Days', '30 - 60 Days', '60 - 90 Days', 'Over 90 Days']
        aging_values = [
            f"{statement_data['total_due']:,.2f}",
            f"{aging['current'] + aging['days_1_30']:,.2f}",
            f"{aging['days_31_60']:,.2f}",
            f"{aging['days_61_90']:,.2f}",
            f"{aging['days_90_plus']:,.2f}"
        ]

        aging_table = Table([aging_header, aging_values], colWidths=[1.4*inch, 1.4*inch, 1.4*inch, 1.4*inch, 1.2*inch])
        aging_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (0, 1), 1, colors.black),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
        ]))
        story.append(aging_table)

        story.append(Spacer(1, 0.3*inch))

        # Interest warning
        story.append(Paragraph("<b>INTEREST AT THE RATE OF 2% WILL BE CHARGED ON UNPAID BALANCE</b>",
                              ParagraphStyle('Warning', fontSize=9)))

        doc.build(story)

    def generate_statement_style4(self, output_path: str, statement_data: dict = None):
        """
        Cinnabar Valley Farms Style - Minimalist professional
        Features: Credit limit, PO# and Terms columns, clean layout
        """
        if statement_data is None:
            statement_data = self._generate_statement_data()

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        story = []

        company = statement_data["company"]
        customer = statement_data["customer"]

        # Header
        header_data = [
            [Paragraph(f"<b>{company['name']}</b>", self.styles['CompanyNameLarge']),
             Paragraph("<b>Statement</b>", ParagraphStyle('RightTitle', alignment=TA_RIGHT, fontSize=20, fontName='Helvetica-Bold'))]
        ]
        header_table = Table(header_data, colWidths=[4*inch, 3*inch])
        story.append(header_table)

        # Company details and date
        left_details = f"""{company['address'].replace(chr(10), '<br/>')}<br/>
        Phone: {company.get('phone', '')} Fax: {company.get('phone', '').replace('555', '556')}<br/>
        {company.get('website', '')}<br/><br/>
        <b>{company.get('email', '')}</b>"""

        right_details = f"""{statement_data['statement_date']}<br/><br/>
        Page 1 of 1<br/><br/>
        {customer['account']}"""

        details_table = Table([
            [Paragraph(left_details, self.styles['Normal']), Paragraph(right_details, self.styles['RightAlign'])]
        ], colWidths=[4*inch, 3*inch])
        story.append(details_table)

        story.append(Spacer(1, 0.3*inch))

        # Customer info
        story.append(Paragraph(f"<b>{customer['name']}</b>", self.styles['Normal']))
        for line in customer['address'].split('\n'):
            story.append(Paragraph(line, self.styles['Normal']))

        story.append(Spacer(1, 0.3*inch))

        # Credit limit
        credit_limit = random.uniform(5000, 50000)
        story.append(Paragraph(f"CREDIT LIMIT    {credit_limit:,.2f}", self.styles['Normal']))

        story.append(Spacer(1, 0.2*inch))

        # Transaction table
        table_data = [['Date', 'Description', 'Invoice #', 'PO#', 'Terms', 'Amount', 'Outstanding']]

        for trans in statement_data['transactions']:
            desc = "Invoice" if trans['is_debit'] else "Credit memo"
            amount = trans['amount'] if trans['is_debit'] else -trans['amount']
            terms = "Net 30 Days"

            table_data.append([
                trans['date'].replace('/', ' '),
                desc,
                trans['reference'],
                trans.get('po_number', ''),
                terms,
                f"{amount:,.2f}",
                f"{trans['balance_after']:,.2f}"
            ])

        trans_table = Table(table_data, colWidths=[0.8*inch, 1*inch, 1.2*inch, 1.2*inch, 1*inch, 0.9*inch, 1*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8E8E8')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (-2, 1), (-1, -1), 'RIGHT'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(trans_table)

        story.append(Spacer(1, 0.5*inch))

        # Aging at bottom
        aging = statement_data['aging']
        aging_data = [
            ['Current', 'Over 30', 'Over 60', 'Over 90', 'Over 120', '', 'Total Due'],
            [f"{aging['current']:,.2f}", f"{aging['days_1_30']:,.2f}", f"{aging['days_31_60']:,.2f}",
             f"{aging['days_61_90']:,.2f}", f"{aging['days_90_plus']:,.2f}", '', f"{statement_data['total_due']:,.2f}"]
        ]

        aging_table = Table(aging_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 0.5*inch, 1.3*inch])
        aging_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
        ]))
        story.append(aging_table)

        doc.build(story)

    def generate_statement_style5(self, output_path: str, statement_data: dict = None):
        """
        Briggs Equipment Style - Bold corporate with colored header
        Features: Large branded header, aging at top, days past due column
        """
        if statement_data is None:
            statement_data = self._generate_statement_data()

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.3*inch,
            bottomMargin=0.5*inch
        )

        story = []

        company = statement_data["company"]
        customer = statement_data["customer"]

        # Bold header banner
        header_table = Table([
            [Paragraph(f"<font color='white' size='24'><b>{company['name'].upper()}</b></font>", self.styles['Normal']),
             Paragraph(f"<font color='black' size='28'><b>STATEMENT</b></font>", self.styles['RightAlign'])]
        ], colWidths=[4*inch, 3.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#8B0000')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(header_table)

        story.append(Spacer(1, 0.1*inch))

        # Date and page info
        date_info = Table([
            [statement_data['statement_date'], 'PAGE 1 OF 1']
        ], colWidths=[3.5*inch, 3.5*inch])
        date_info.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(date_info)

        # Remit to and correspondence addresses
        addresses = Table([
            [Paragraph(f"<b>REMIT TO:</b><br/>{company['name']}<br/>{company['address'].replace(chr(10), '<br/>')}", self.styles['Normal']),
             Paragraph(f"<b>CORRESPONDENCE TO:</b><br/>{company['name']}<br/>{company['address'].replace(chr(10), '<br/>')}", self.styles['Normal'])]
        ], colWidths=[3.5*inch, 3.5*inch])
        addresses.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFE4E1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(addresses)

        story.append(Spacer(1, 0.2*inch))

        # Account and sold to
        story.append(Paragraph(f"ACCOUNT NUMBER: {customer['account']}", self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("<b>SOLD TO</b>", self.styles['Normal']))
        story.append(Paragraph(customer['name'], self.styles['Normal']))
        for line in customer['address'].split('\n'):
            story.append(Paragraph(line, self.styles['Normal']))

        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>QUESTIONS CALL:</b> {company.get('phone', '')}", self.styles['Normal']))

        story.append(Spacer(1, 0.2*inch))

        # Aging buckets in colored table at TOP
        aging = statement_data['aging']
        aging_headers = ['Balance', 'CURRENT', '1-30 Days Past Due', '31-60 Days Past Due', '61-90 Days Past Due', '91-150 Days Past Due', '150+ Days Past Due']
        aging_values = [
            f"${statement_data['total_due']:,.2f}",
            f"${aging['current']:,.2f}",
            f"${aging['days_1_30']:,.2f}",
            f"${aging['days_31_60']:,.2f}",
            f"${aging['days_61_90']:,.2f}",
            f"${aging['days_90_plus'] * 0.6:,.2f}",
            f"${aging['days_90_plus'] * 0.4:,.2f}"
        ]

        aging_table = Table([aging_headers, aging_values], colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        aging_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFFACD')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(aging_table)

        story.append(Spacer(1, 0.2*inch))

        # Transaction table with days past due
        table_data = [['INVOICED', 'DUE', 'INVOICE REFERENCES', 'CUSTOMER REF. NO.', 'INVOICE AMOUNT', 'BALANCE DUE', 'PAST DUE']]

        today = datetime.now()
        for trans in statement_data['transactions']:
            days_past = (today - trans['date_obj']).days
            past_due_str = f"{days_past} DAYS" if days_past > 0 else ""

            amount = trans['amount'] if trans['is_debit'] else -trans['amount']

            table_data.append([
                trans['date'],
                trans['due_date'],
                trans['reference'],
                trans.get('po_number', ''),
                f"{amount:,.2f}",
                f"{trans['balance_after']:,.2f}",
                past_due_str
            ])

        trans_table = Table(table_data, colWidths=[0.9*inch, 0.9*inch, 1.3*inch, 1.3*inch, 1.1*inch, 1*inch, 0.8*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFFFE0')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (-3, 1), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF8DC')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(trans_table)

        story.append(Spacer(1, 0.3*inch))

        # Terms and appreciation message
        story.append(Paragraph("Terms: Net 30 Days, unless otherwise prior specified in writing.", self.styles['SmallText']))
        story.append(Paragraph("Invoices are deemed correct unless errors are reported in writing within 15 days of invoice date.", self.styles['SmallText']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("<b>We Appreciate Your Business!</b>", ParagraphStyle('Center', alignment=TA_CENTER, fontSize=12)))

        doc.build(story)

    def _generate_statement_data(self, num_transactions=10):
        """Generate complete statement data"""
        company = self.data_generator.generate_company()
        customer = self.data_generator.generate_customer()

        opening_balance = random.uniform(0, 10000)
        transactions, closing_balance = self.data_generator.generate_transactions(num_transactions, opening_balance)
        aging = self.data_generator.calculate_aging(transactions)

        return {
            "company": company,
            "customer": customer,
            "statement_number": f"{random.randint(10000, 99999)}",
            "statement_date": datetime.now().strftime("%d/%m/%Y"),
            "transactions": transactions,
            "total_due": closing_balance,
            "aging": aging
        }

    def generate_batch(self, output_dir: str = "generated_statements", count: int = 25, save_ground_truth: bool = True):
        """Generate a batch of statements in various styles with ground truth

        Args:
            output_dir: Directory to save generated files
            count: Number of statements to generate
            save_ground_truth: If True, save JSON ground truth alongside each PDF
        """
        os.makedirs(output_dir, exist_ok=True)

        styles = [
            (self.generate_statement_style1, "SheldonCreek"),
            (self.generate_statement_style2, "CulturesGenV"),
            (self.generate_statement_style3, "ComeauSeaFoods"),
            (self.generate_statement_style4, "CinnabarValley"),
            (self.generate_statement_style5, "BriggsEquipment"),
        ]

        generated = []
        for i in range(count):
            style_func, style_name = styles[i % len(styles)]
            output_path = os.path.join(output_dir, f"statement_{i+1:03d}_{style_name}.pdf")

            try:
                # Generate statement data
                statement_data = self._generate_statement_data()

                # Generate PDF with this data
                style_func(output_path, statement_data)

                # Save ground truth if requested
                if save_ground_truth:
                    ground_truth = self._create_ground_truth(statement_data, style_name)
                    ground_truth_path = output_path.replace('.pdf', '_ground_truth.json')
                    with open(ground_truth_path, 'w') as f:
                        json.dump(ground_truth, f, indent=2, default=str)

                generated.append(output_path)
                print(f"Generated: {output_path}")
                if save_ground_truth:
                    print(f"  Ground truth: {ground_truth_path}")
            except Exception as e:
                print(f"Error generating {output_path}: {e}")

        return generated

    def _create_ground_truth(self, statement_data: dict, style_name: str) -> dict:
        """Create comprehensive ground truth labels for a statement"""

        # Extract credit items
        credit_items = []
        for trans in statement_data['transactions']:
            if trans.get('is_credit') and not trans.get('is_debit'):
                credit_items.append({
                    'reference': trans['reference'],
                    'date': trans['date'],
                    'amount': trans['amount'],
                    'type': trans['type'],
                    'description': trans.get('description', ''),
                })

        # Calculate summary statistics
        total_debits = sum(t['amount'] for t in statement_data['transactions'] if t.get('is_debit'))
        total_credits = sum(t['amount'] for t in statement_data['transactions'] if t.get('is_credit') and not t.get('is_debit'))

        ground_truth = {
            'metadata': {
                'statement_number': statement_data.get('statement_number', ''),
                'statement_date': statement_data.get('statement_date', ''),
                'pdf_style': style_name,
                'generated_at': datetime.now().isoformat(),
            },
            'company': {
                'name': statement_data['company']['name'],
                'address': statement_data['company']['address'],
                'phone': statement_data['company'].get('phone', ''),
                'email': statement_data['company'].get('email', ''),
            },
            'customer': {
                'name': statement_data['customer']['name'],
                'address': statement_data['customer']['address'],
                'account': statement_data['customer']['account'],
            },
            'balances': {
                'total_due': statement_data['total_due'],
                'aging': statement_data['aging'],
            },
            'transactions': statement_data['transactions'],
            'ground_truth_labels': {
                'credit_items': credit_items,
                'num_credits': len(credit_items),
                'total_credit_amount': total_credits,
                'total_debit_amount': total_debits,
                'num_transactions': len(statement_data['transactions']),
                'transaction_types': {
                    'invoices': len([t for t in statement_data['transactions'] if t['type'] == 'invoice']),
                    'credit_notes': len([t for t in statement_data['transactions'] if t['type'] == 'credit_note']),
                    'payments': len([t for t in statement_data['transactions'] if t['type'] == 'payment']),
                    'debit_notes': len([t for t in statement_data['transactions'] if t['type'] == 'debit_note']),
                },
            },
        }

        return ground_truth


# Main execution
if __name__ == '__main__':
    print("Generating 25 realistic supplier statements...")
    print("=" * 50)

    pdf_gen = StatementPDFGenerator()
    generated_files = pdf_gen.generate_batch(count=25)

    print("=" * 50)
    print(f"Successfully generated {len(generated_files)} statements")
    print(f"Output directory: generated_statements/")
