# Synthetic Supplier Statement PDF Generator

A Python framework for generating realistic supplier statement PDFs with comprehensive ground truth labels. Designed for training and evaluating AI/ML models in Accounts Payable automation, particularly for credit reconciliation and document understanding tasks.

## Features

- **5 Distinct PDF Styles**: Generates statements mimicking real-world supplier formats
- **Realistic Data Generation**: Canadian suppliers, major retailers, authentic transaction flows
- **Comprehensive Ground Truth**: JSON labels for every generated PDF with transaction details, credit items, and aging information
- **Optional OpenAI Enhancement**: Uses GPT-3.5-turbo for more varied company data generation (falls back to built-in data)
- **Batch Generation**: Generate multiple statements at once with automatic style rotation

## Installation

```bash
pip install -r requirements.txt
```

Required packages:
- `reportlab>=4.0.0` - PDF generation
- `python-dotenv>=1.0.0` - Environment variable management
- `openai>=1.0.0` - Optional AI-enhanced data generation

## Quick Start

```bash
# Generate 25 statements with ground truth
python3 statement_pdf_generator.py
```

This creates a `generated_statements/` directory containing:
- PDF files for each statement
- JSON ground truth files with matching names

## PDF Statement Styles

The generator produces 5 distinct statement layouts:

1. **SheldonCreek** - Clean professional format with aging at bottom
2. **CulturesGenV** - Corporate multi-page format with document type codes
3. **ComeauSeaFoods** - Bold branding with debit/credit columns and running balance
4. **CinnabarValley** - Minimalist professional with credit limit and PO# columns
5. **BriggsEquipment** - Bold corporate with colored header and days past due tracking

## Ground Truth Structure

Each PDF is paired with a JSON file containing:

```json
{
  "metadata": {
    "statement_number": "12345",
    "statement_date": "17/11/2025",
    "pdf_style": "SheldonCreek",
    "generated_at": "2025-11-17T10:30:00"
  },
  "company": {
    "name": "Northern Foods Supply Co.",
    "address": "1234 Industrial Blvd\nToronto ON M5V 2T6",
    "phone": "(416) 555-0123",
    "email": "ar@northernfoods.ca"
  },
  "customer": {
    "name": "SOBEYS INC.",
    "address": "115 King Street\nStellarton NS B0K 1S0",
    "account": "SOB001"
  },
  "balances": {
    "total_due": 15234.56,
    "aging": {
      "current": 5000.00,
      "days_1_30": 3500.00,
      "days_31_60": 2500.00,
      "days_61_90": 1500.00,
      "days_90_plus": 2734.56
    }
  },
  "transactions": [
    {
      "date": "01/09/2025",
      "type": "invoice",
      "reference": "INV45678",
      "amount": 12500.00,
      "is_credit": false,
      "is_debit": true,
      "po_number": "PO123456",
      "due_date": "01/10/2025"
    }
  ],
  "ground_truth_labels": {
    "credit_items": [
      {
        "reference": "CN12345",
        "date": "15/09/2025",
        "amount": 500.00,
        "type": "credit_note",
        "description": "Returned goods"
      }
    ],
    "num_credits": 1,
    "total_credit_amount": 500.00,
    "total_debit_amount": 16234.56,
    "num_transactions": 10,
    "transaction_types": {
      "invoices": 5,
      "credit_notes": 1,
      "payments": 3,
      "debit_notes": 1
    }
  }
}
```

## Programmatic Usage

```python
from statement_pdf_generator import StatementPDFGenerator

# Initialize generator
pdf_gen = StatementPDFGenerator()

# Generate a batch of statements
generated_files = pdf_gen.generate_batch(
    output_dir="my_statements",
    count=50,
    save_ground_truth=True
)

# Generate a single statement with specific style
statement_data = pdf_gen._generate_statement_data(num_transactions=15)
pdf_gen.generate_statement_style1("output.pdf", statement_data)

# Access ground truth for ML training
ground_truth = pdf_gen._create_ground_truth(statement_data, "SheldonCreek")
```

## Transaction Types

- **Invoice (IN)** - Debit entry for goods/services provided
- **Credit Note (CN)** - Credit entry for returns, adjustments, discounts
- **Payment (PY)** - Credit entry for received payments
- **Debit Note (DN)** - Additional debit charges

## Use Cases

- **OCR Training**: Test document text extraction accuracy
- **Credit Detection**: Train models to identify credit notes and payments
- **Amount Extraction**: Evaluate numerical data extraction precision
- **Balance Reconciliation**: Validate automated balance verification systems
- **Document Classification**: Train models to recognize different statement formats

## OpenAI Integration (Optional)

For enhanced data variety, set your OpenAI API key:

```bash
export OPENAI_API_KEY=your_key_here
```

Or create a `.env` file:

```
OPENAI_API_KEY=your_key_here
```

The generator will automatically use GPT-3.5-turbo for company data generation when available, falling back to built-in realistic Canadian business data otherwise.

## Output Structure

```
generated_statements/
├── statement_001_SheldonCreek.pdf
├── statement_001_SheldonCreek_ground_truth.json
├── statement_002_CulturesGenV.pdf
├── statement_002_CulturesGenV_ground_truth.json
├── statement_003_ComeauSeaFoods.pdf
├── statement_003_ComeauSeaFoods_ground_truth.json
└── ...
```

## License

See [LICENSE](LICENSE) for details.
