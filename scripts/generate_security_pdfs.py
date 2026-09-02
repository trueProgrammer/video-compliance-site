#!/usr/bin/env python3
"""Generate the public Vidcomply security overview and sample DPA PDFs."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    PageTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "pdf"
ARCHITECTURE_IMAGE = ROOT / "security" / "assets" / "aws-marketplace-deployment-architecture.png"

INK = colors.HexColor("#162033")
MUTED = colors.HexColor("#5f6b7a")
BLUE = colors.HexColor("#1d63ed")
PALE_BLUE = colors.HexColor("#edf4ff")
PALE_GREEN = colors.HexColor("#eaf8f3")
GREEN = colors.HexColor("#08765c")
LINE = colors.HexColor("#dbe3ee")
PAPER = colors.HexColor("#f7f9fc")
WHITE = colors.white


def stylesheet():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=32,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=17,
            textColor=MUTED,
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=23,
            textColor=INK,
            spaceBefore=4,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=INK,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=14,
            textColor=colors.HexColor("#263347"),
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.6,
            leading=10.5,
            textColor=MUTED,
        ),
        "label": ParagraphStyle(
            "Label",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9,
            textColor=BLUE,
            spaceAfter=6,
        ),
        "card_title": ParagraphStyle(
            "CardTitle",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=INK,
            spaceAfter=4,
        ),
        "card_body": ParagraphStyle(
            "CardBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.3,
            leading=12,
            textColor=MUTED,
        ),
        "cover_note": ParagraphStyle(
            "CoverNote",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=13,
            textColor=GREEN,
            alignment=TA_CENTER,
        ),
    }


STYLES = stylesheet()


def header_footer(canvas, doc, document_label):
    canvas.saveState()
    width, height = letter
    canvas.setFillColor(INK)
    canvas.rect(0, height - 0.08 * inch, width, 0.08 * inch, stroke=0, fill=1)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(INK)
    canvas.drawString(0.65 * inch, height - 0.42 * inch, "VIDCOMPLY")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - 0.65 * inch, height - 0.42 * inch, document_label)
    canvas.setStrokeColor(LINE)
    canvas.line(0.65 * inch, 0.55 * inch, width - 0.65 * inch, 0.55 * inch)
    canvas.setFont("Helvetica", 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.65 * inch, 0.32 * inch, "Public customer-neutral document | 2 September 2026")
    canvas.drawRightString(width - 0.65 * inch, 0.32 * inch, f"Page {doc.page}")
    canvas.restoreState()


def doc_template(path, title, document_label):
    doc = BaseDocTemplate(
        str(path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.82 * inch,
        bottomMargin=0.88 * inch,
        title=title,
        author="AGENTIC VISION LTD (trading as Vidcomply)",
        subject="Vidcomply public security documentation",
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="content",
    )

    def draw_frame(canvas, document):
        header_footer(canvas, document, document_label)

    doc.addPageTemplates([PageTemplate(id="all-pages", frames=[frame], onPage=draw_frame)])
    return doc


def p(text, style="body"):
    return Paragraph(text, STYLES[style])


def bullet(text):
    return Paragraph(f"<font color='#1d63ed'>&#8226;</font>&nbsp;&nbsp;{text}", STYLES["body"])


def info_card(label, title, body, fill=WHITE):
    card = Table(
        [[p(label.upper(), "label")], [p(title, "card_title")], [p(body, "card_body")]],
        colWidths=[3.15 * inch],
    )
    card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), fill),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 2), (-1, -1), 11),
                ("TOPPADDING", (0, 1), (-1, 2), 0),
                ("BOTTOMPADDING", (0, 0), (-1, 1), 3),
            ]
        )
    )
    return card


def build_security_overview():
    path = OUTPUT_DIR / "VidComply_Security_Architecture_Overview.pdf"
    doc = doc_template(path, "Vidcomply Security & Architecture Overview", "Security & Architecture Overview")
    story = []

    story.extend(
        [
            Spacer(1, 0.35 * inch),
            p("SECURITY &amp; TRUST", "label"),
            p("Vidcomply Security &amp;<br/>Architecture Overview", "title"),
            p(
                "A customer-neutral summary of how Vidcomply protects media assets, personal data, "
                "processing environments, and compliance outputs.",
                "subtitle",
            ),
            Spacer(1, 0.08 * inch),
            Table(
                [[
                    info_card("01", "Buyer-owned source", "Source media can remain in customer-controlled storage; Vidcomply receives only required permissions.", PALE_BLUE),
                    info_card("02", "Isolated workloads", "Dedicated processing resources, separate queues, least-privilege IAM, and network controls.", PALE_GREEN),
                ], [
                    info_card("03", "Agreed region", "Deployment location is agreed for residency, security, and latency requirements.", WHITE),
                    info_card("04", "No model training", "Customer content is processed only for the contracted service and is not used to improve models.", WHITE),
                ], [
                    info_card("05", "Auditable activity", "Outputs, processing records, and relevant audit logs can be provided under the agreed access model.", WHITE),
                    info_card("06", "Controlled retention", "Temporary processing files follow contract-defined lifecycle, return, and deletion procedures.", WHITE),
                ]],
                colWidths=[3.28 * inch, 3.28 * inch],
                hAlign="LEFT",
                style=TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]),
            ),
            Spacer(1, 0.14 * inch),
            Table(
                [[p("PUBLIC SUMMARY", "cover_note")]],
                colWidths=[6.45 * inch],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), PALE_GREEN),
                    ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#b9e5d8")),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]),
            ),
            Spacer(1, 0.16 * inch),
            p(
                "This document describes Vidcomply's standard control approach. Customer-specific architecture, "
                "service providers, regions, and contractual commitments are defined in the applicable Order Form, "
                "DPA, and Security Schedule.",
                "small",
            ),
            PageBreak(),
            p("01 / REFERENCE ARCHITECTURE", "label"),
            p("AWS Marketplace deployment pattern", "h1"),
            p(
                "Vidcomply is available through AWS Marketplace. The primary enterprise pattern keeps source media "
                "in buyer-controlled Amazon S3 storage, grants only the minimum cross-account permissions required, "
                "runs dedicated seller-side processing, and writes reports back to the buyer's designated location.",
            ),
        ]
    )

    img = Image(str(ARCHITECTURE_IMAGE))
    img.drawHeight = 3.1 * inch
    img.drawWidth = 5.52 * inch
    story.extend(
        [
            Spacer(1, 0.08 * inch),
            img,
            Spacer(1, 0.12 * inch),
            p(
                "Reference architecture shown for illustration. The deployment region, customer storage model, "
                "enabled services, and integration boundaries are agreed during onboarding.",
                "small",
            ),
            Spacer(1, 0.08 * inch),
            Table(
                [[p("CUSTOMER CONTROL", "label")], [p("<font color='#ffffff'>Buyer-owned source storage  |  Dedicated processing  |  Agreed data residency  |  Auditable access  |  No model training  |  Contractual deletion</font>", "card_title")]],
                colWidths=[6.0 * inch],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), INK),
                    ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 9),
                ]),
            ),
            Spacer(1, 0.1 * inch),
            p("Core flow", "h2"),
            bullet("A customer-owned storage event initiates a controlled processing job."),
            bullet("Least-privilege IAM access is scoped to agreed source and report locations."),
            bullet("Processing runs inside an isolated Amazon VPC with restricted ingress and controlled egress."),
            bullet("Optional enterprise AI services receive only approved data segments where required."),
            PageBreak(),
            p("02 / SECURITY CONTROLS", "label"),
            p("Six customer security promises", "h1"),
        ]
    )

    control_rows = [
        ("Source control", "Media can remain in buyer-owned storage. Vidcomply receives only the minimum permissions required to process the asset and return results."),
        ("Workload isolation", "Dedicated processing resources and separate queues are protected with least-privilege IAM and network controls. Dedicated-account deployment is available where required."),
        ("Region choice", "Deployment region is agreed before onboarding based on data-residency, security, and latency requirements."),
        ("No AI training", "Customer content is processed solely for the contracted service and is subject to equivalent no-training controls at approved AI subprocessors."),
        ("Auditability", "Processing, infrastructure, and access activity are logged. Relevant outputs, processing records, and audit logs can be provided under the agreed access model."),
        ("Retention control", "Temporary files are lifecycle-controlled. Retention, return, and deletion procedures are agreed contractually."),
    ]
    table_data = [[p("Control", "card_title"), p("Standard approach", "card_title")]] + [
        [p(a, "card_title"), p(b, "card_body")] for a, b in control_rows
    ]
    controls = Table(table_data, colWidths=[1.65 * inch, 4.8 * inch], repeatRows=1)
    controls.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PAPER]),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend(
        [
            controls,
            Spacer(1, 0.18 * inch),
            p("Shared responsibility", "h2"),
            p(
                "AWS and approved service providers protect their underlying services under their own assurance "
                "programmes. Vidcomply configures and operates the application controls. Customers control their "
                "users, source-content permissions, approved workflows, and contractual deployment choices.",
            ),
            p(
                "Customers are not granted broad administrative access to Vidcomply's shared AWS account. Read-only "
                "infrastructure visibility or dedicated-account deployment can be provided where required and agreed.",
                "small",
            ),
            PageBreak(),
            p("03 / GOVERNANCE &amp; ASSURANCE", "label"),
            p("Evidence, ownership, and due diligence", "h1"),
            p("Customer content governance", "h2"),
            bullet("The customer retains ownership of its source content and Vidcomply-generated outputs."),
            bullet("Processing is limited to providing the contracted compliance service."),
            bullet("Data residency, retention, deletion, and transfer safeguards are recorded contractually."),
            bullet("Subprocessors are disclosed and bound by relevant confidentiality and data-protection terms."),
            Spacer(1, 0.08 * inch),
            p("AWS assurance", "h2"),
            p(
                "Vidcomply completed a review in the AWS Well-Architected Tool on 5 June 2026 against the "
                "AWS Well-Architected Framework version dated 25 February 2025. All questions were answered across "
                "the four assessed pillars: Operational Excellence, Security, Reliability, and Performance Efficiency. "
                "The report recorded no high-risk improvement items and identified medium-risk opportunities tracked "
                "through an improvement plan. Cost Optimization and Sustainability were not assessed in that review.",
            ),
            p(
                "The review is an architecture-assessment and improvement exercise; it is not an AWS certification. "
                "The full report and detailed customer architecture are available to qualified security teams during "
                "due diligence, subject to confidentiality controls.",
                "small",
            ),
            Spacer(1, 0.12 * inch),
            p("Available diligence material", "h2"),
            bullet("Sample Data Processing Agreement and current subprocessor overview."),
            bullet("Detailed AWS Well-Architected Tool report under NDA."),
            bullet("Customer-specific deployment architecture and security schedule."),
            bullet("Security questionnaires and additional evidence on request."),
            Spacer(1, 0.14 * inch),
            Table(
                [[p("SECURITY CONTACT", "label")], [p("support@vidcomply.ai", "card_title")], [p("Report security concerns or request enterprise due-diligence material.", "card_body")]],
                colWidths=[6.45 * inch],
                style=TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE),
                    ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#c8d9fb")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 14),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                    ("TOPPADDING", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 2), (-1, -1), 12),
                ]),
            ),
        ]
    )

    doc.build(story)
    return path


def section(title, paragraphs):
    items = [p(title, "h2")]
    for paragraph in paragraphs:
        items.append(p(paragraph))
    return KeepTogether(items)


def build_sample_dpa():
    path = OUTPUT_DIR / "VidComply_Sample_Data_Processing_Agreement.pdf"
    doc = doc_template(path, "Vidcomply Sample Data Processing Agreement", "Sample Data Processing Agreement")
    story = [
        Spacer(1, 0.25 * inch),
        p("SAMPLE TEMPLATE", "label"),
        p("Data Processing Agreement", "title"),
        p("AGENTIC VISION LTD (trading as Vidcomply)", "subtitle"),
        Table(
            [[p("This public sample is provided for discussion and is subject to legal review, negotiation, and execution. It does not create binding obligations until signed by both parties.", "cover_note")]],
            colWidths=[6.45 * inch],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), PALE_GREEN),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#b9e5d8")),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]),
        ),
        Spacer(1, 0.2 * inch),
        p(
            "This Data Processing Agreement (\"Agreement\") is made as of <b>[Effective Date]</b> between "
            "<b>[Data Controller]</b>, of <b>[Controller Address]</b> (\"Controller\"), and AGENTIC VISION LTD "
            "(trading as Vidcomply), 14 East Bay Lane, London, E15 2GW, Company No. 16720340 (\"Processor\"). "
            "Controller and Processor are together the \"Parties\".",
        ),
        HRFlowable(width="100%", thickness=0.7, color=LINE, spaceBefore=5, spaceAfter=8),
    ]

    clauses = [
        ("1. Definitions", [
            "<b>1.1 Data Protection Laws</b> means applicable laws and regulations relating to personal data and privacy, including the UK GDPR, EU GDPR, the Data Protection Act 2018, and applicable United States privacy laws.",
            "<b>1.2 Personal Data</b> means information relating to an identified or identifiable natural person.",
            "<b>1.3 Processing</b> means any operation performed on Personal Data, including collection, storage, use, disclosure, restriction, erasure, or destruction.",
            "<b>1.4 Subprocessor</b> means a third party appointed by Processor to process Personal Data for Controller.",
            "<b>1.5 Main Agreement</b> means the principal agreement between Controller and Processor to which this Agreement relates.",
        ]),
        ("2. Subject Matter and Duration", [
            "<b>2.1 Subject Matter.</b> This Agreement governs Processor's processing of Personal Data on behalf of Controller as described in Appendix A for the provision of media-compliance services, including ingestion, storage, analysis, and compliance verification using automated tools and AI models.",
            "<b>2.2 Duration.</b> This Agreement begins on the Effective Date and continues until the Main Agreement ends, unless otherwise specified in Appendix A or terminated under Section 12.",
        ]),
        ("3. Data Processing", [
            "<b>3.1 Instructions.</b> Processor will process Personal Data only as necessary to perform the Main Agreement and on Controller's documented instructions, unless applicable law requires otherwise. Where permitted, Processor will inform Controller of that legal requirement before processing.",
            "<b>3.2 Restriction on AI Training.</b> Processor will not use Controller's Personal Data, uploaded video or audio, or outputs to train, retrain, or improve Processor's base AI or ML models. Processor will apply equivalent restrictions to Subprocessors where such contractual controls are available.",
            "<b>3.3 Compliance.</b> Processor will comply with applicable Data Protection Laws and the principles of lawfulness, fairness, transparency, purpose limitation, data minimisation, accuracy, storage limitation, integrity, and confidentiality.",
            "<b>3.4 Confidentiality.</b> Processor will ensure authorised personnel are bound by confidentiality obligations and will maintain appropriate confidentiality procedures.",
        ]),
        ("4. Data Subject Rights", [
            "<b>4.1 Assistance.</b> Taking into account the nature of processing, Processor will reasonably assist Controller, at Controller's cost where applicable, with requests concerning access, correction, erasure, restriction, portability, objection, and automated decision-making rights.",
            "<b>4.2 Requests.</b> Processor will promptly notify Controller of a Data Subject request concerning Controller Personal Data and will respond only on Controller's documented instructions or as required by law.",
        ]),
        ("5. Security Measures", [
            "<b>5.1 Technical and Organisational Measures.</b> Processor will maintain measures appropriate to risk, including encryption in transit and at rest; access controls; isolated processing and storage; resilience and recovery procedures; and processes for evaluating control effectiveness. The customer-specific deployment and any dedicated resources are defined in the applicable Order Form or Security Schedule.",
            "<b>5.2 Assessments and Audits.</b> On reasonable prior notice and during normal business hours, Controller may request information reasonably necessary to demonstrate compliance. Audits will be coordinated to avoid unnecessary disruption and remain subject to confidentiality, security, and cost arrangements in the Main Agreement.",
        ]),
        ("6. Subprocessing", [
            "<b>6.1 Authorisation.</b> Controller authorises Processor to engage the Subprocessors identified through Processor's current subprocessor notice and customer documentation. Processor will provide notice of material changes and an opportunity to object on reasonable data-protection grounds as agreed in the Main Agreement.",
            "<b>6.2 Flow-down and Liability.</b> Processor will impose materially equivalent data-protection obligations on each Subprocessor and remains responsible for its Subprocessors' performance to the extent required by Data Protection Laws.",
        ]),
        ("7. International Transfers", [
            "<b>7.1 Locations.</b> Hosting region, processing locations, and approved international transfers will be specified in the Order Form, Security Schedule, or current subprocessor notice applicable to Controller's deployment.",
            "<b>7.2 Safeguards.</b> Processor will implement an appropriate transfer mechanism where Data Protection Laws require one, such as adequacy regulations, the UK International Data Transfer Addendum, or approved Standard Contractual Clauses.",
        ]),
        ("8. Personal Data Breach", [
            "<b>8.1 Notification.</b> Processor will notify Controller without undue delay after becoming aware of a Personal Data breach affecting Controller Personal Data and, where contractually agreed, within 72 hours. Notification will include available details about the nature, scope, likely consequences, contact point, and mitigation measures.",
            "<b>8.2 Cooperation.</b> Processor will take reasonable corrective action and cooperate with Controller's lawful response, mitigation, and notification obligations.",
        ]),
        ("9. Retention, Return, and Deletion", [
            "<b>9.1 Retention.</b> Processor will retain Personal Data only for the period agreed in the Main Agreement, Order Form, or Security Schedule, or as required by law.",
            "<b>9.2 Return or Deletion.</b> At the end of the Main Agreement or on Controller's written request, Processor will return or delete Controller Personal Data as instructed, unless law requires retention. Processor will provide written confirmation within the contractually agreed period, which is ordinarily 30 days.",
        ]),
        ("10. Liability and Indemnity", [
            "<b>10.1 Liability.</b> Each Party's liability under this Agreement is subject to the limitations and exclusions in the Main Agreement, except where liability cannot lawfully be limited.",
            "<b>10.2 Indemnity.</b> Any indemnity concerning a breach of this Agreement will be governed by the Main Agreement and applicable law.",
        ]),
        ("11. General", [
            "<b>11.1 Amendments.</b> Amendments must be in writing and signed by both Parties, except updates expressly permitted under the Main Agreement.",
            "<b>11.2 Governing Law.</b> Unless the Main Agreement states otherwise, this Agreement is governed by the laws of England and Wales and the courts specified in the Main Agreement have jurisdiction.",
            "<b>11.3 Confidentiality.</b> Each Party will protect confidential information received under this Agreement and disclose it only as permitted by the Main Agreement or required by law.",
            "<b>11.4 Severability and Notices.</b> Invalid terms will be interpreted or severed without affecting remaining terms. Notices must be provided using the method specified in the Main Agreement.",
        ]),
        ("12. Termination", [
            "<b>12.1 Relationship to Main Agreement.</b> This Agreement terminates when Processor has ceased processing Controller Personal Data after termination or expiry of the Main Agreement, unless the Parties agree otherwise.",
            "<b>12.2 Survival.</b> Confidentiality, return or deletion, audit, liability, and other provisions intended by their nature to survive will remain effective.",
        ]),
    ]

    for title, paragraphs in clauses:
        story.append(section(title, paragraphs))

    story.extend([
        PageBreak(),
        p("SIGNATURES", "label"),
        p("Execution", "h1"),
        p("The Parties have executed this Data Processing Agreement as of the Effective Date."),
        Spacer(1, 0.22 * inch),
        Table(
            [
                [p("CONTROLLER", "label"), p("PROCESSOR", "label")],
                [p("[Controller legal name]<br/><br/>Name: __________________________<br/><br/>Title: ___________________________<br/><br/>Date: ____________________________", "body"),
                 p("AGENTIC VISION LTD<br/>(trading as Vidcomply)<br/><br/>Name: __________________________<br/><br/>Title: ___________________________<br/><br/>Date: ____________________________", "body")],
            ],
            colWidths=[3.2 * inch, 3.2 * inch],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.7, LINE),
                ("BACKGROUND", (0, 0), (-1, 0), PALE_BLUE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]),
        ),
        PageBreak(),
        p("APPENDIX A", "label"),
        p("Details of Processing", "h1"),
        section("1. Nature and Purpose", [
            "Processor provides media-compliance services to Controller. Processing may include secure ingestion, storage, analysis, and generation of compliance evidence, reports, alerts, or approved workflow outputs.",
            "The enabled processing stages, data flows, and integrations are limited to the services selected in the Order Form or Security Schedule.",
        ]),
        section("2. Duration and Retention", [
            "Processing continues for the term of the Main Agreement. Retention periods are specified in the Order Form or Security Schedule. At the end of the agreed period, Personal Data is returned or securely deleted, subject to legal retention obligations.",
        ]),
        section("3. Categories of Data Subjects", [
            "Individuals appearing or heard in customer-provided media; customer personnel and authorised users; and other individuals whose Personal Data is included in customer-provided content or metadata.",
        ]),
        section("4. Types of Personal Data", [
            "Video and audio recordings; images, voices, actions, and contextual identifiers; media metadata; transcripts and derived analysis; and authorised user account information. Special-category or sensitive data may be processed only where present in customer-provided content and lawfully instructed by Controller.",
        ]),
        section("5. Hosting Region and Data Residency", [
            "<b>Hosting region:</b> As specified in the applicable Order Form or Security Schedule.<br/><b>Data residency and transfers:</b> As specified for the selected deployment and approved services. Customer-specific commitments take precedence over this sample.",
        ]),
        section("6. Approved Subprocessors", [
            "The current public overview is maintained at <b>https://www.vidcomply.ai/security/subprocessors.html</b>. The customer-specific list, permitted purposes, locations, and transfer safeguards are confirmed in the Order Form, Security Schedule, or executed DPA.",
        ]),
        section("7. Technical and Organisational Measures", [
            "Measures may include TLS 1.2+ in transit; AES-256 or AWS KMS-backed encryption at rest; logically isolated storage and processing; dedicated resources where agreed; MFA and role-based access; restricted administrative access; infrastructure and API logging; controlled network ingress and egress; recovery procedures; vulnerability management; and incident-response processes.",
        ]),
        Spacer(1, 0.15 * inch),
        p("CUSTOMER-SPECIFIC SCHEDULE", "label"),
        p("The final executed DPA should attach or reference the applicable Order Form and Security Schedule. Those documents define the actual region, subprocessors, retention period, enabled integrations, security commitments, and any negotiated audit terms.", "small"),
    ])

    doc.build(story)
    return path


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [build_security_overview(), build_sample_dpa()]
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
