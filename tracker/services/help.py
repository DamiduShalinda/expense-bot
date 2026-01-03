def get_help_text() -> str:
    return "\n".join(
        [
            "Supported formats:",
            "- spent 1200 on groceries from hdfc card",
            "- spent 450 on electricity from sbi account",
            "- spent 300 on snacks from wallet cash",
            "- update expense 23 amount 2500 category rent source hdfc card on 2024-09-01",
            "- delete expense 23",
            "- balance of sbi account",
            "- balance of hdfc card",
            "- show expenses for september 2024",
            "- summary expenses this month",
            "- available credit for hdfc card",
            "- list accounts",
            "- show cards",
            "- list transactions",
        ]
    )
