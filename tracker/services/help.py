def get_help_text() -> str:
    return "\n".join(
        [
            "Supported formats:",
            "- spent 1200 on groceries from hdfc card",
            "- spent 450 on electricity from sbi account",
            "- spent 300 on snacks from wallet cash",
            "- spent 900 on fuel from hdfc card last4 1234",
            "- update expense 23 amount 2500 category rent source hdfc card on 2024-09-01",
            "- delete expense 23",
            "- balance of sbi account",
            "- balance of hdfc card last4 1234",
            "- show expenses for september 2024",
            "- summary expenses this month",
            "- available credit for hdfc card",
            "- add account sbi account balance 12000",
            "- add card hdfc limit 50000 cycle 5 last4 1234",
            "- add loan home amount 500000 description home renovation",
            "- pay loan home amount 15000 on 2024-01-15",
            "- list accounts",
            "- show cards",
            "- list categories",
            "- list loans",
            "- list transactions",
        ]
    )
