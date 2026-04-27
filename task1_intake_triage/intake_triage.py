import json
from .utils import (
    load_client_profiles,
    build_prompt,
    call_llm_with_retry,
    generate_docx,
)

from .config import CLIENTS_FILE, OUTPUT_FILE, EVIDENCE_FILE


def run_triage():
    try:
        client_profiles = load_client_profiles(CLIENTS_FILE)
    except Exception as e:
        print(f"Error loading clients: {e}")
        return []

    all_results = []
    evidence_log = []

    for i, client in enumerate(client_profiles, 1):
        print(f"\n[{i}/{len(client_profiles)}] Processing: {client['name']}...")

        prompt = build_prompt(client)

        try:
            result = call_llm_with_retry(prompt)
        except Exception as e:
            print(f"LLM call failed: {e}")
            continue

        parsed = result.model_dump()

        print("Done")
        print(f"Instruments : {parsed['recommended_instruments']}")
        print(f"Urgency     : {parsed['urgency_flag']}")

        all_results.append(parsed)

        evidence_log.append(
            {
                "profile_number": i,
                "input_data": client,
                "prompt_sent": prompt,
                "llm_output": parsed,
            }
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nresults saved to: {OUTPUT_FILE}")

    with open(EVIDENCE_FILE, "w", encoding="utf-8") as f:
        json.dump(evidence_log, f, indent=2, ensure_ascii=False)

    print(f"evidence log saved to: {EVIDENCE_FILE}")

    print("\n\nAll done\n\n")

    generate_docx(evidence_log, EVIDENCE_FILE)
    return all_results


if __name__ == "__main__":
    run_triage()
