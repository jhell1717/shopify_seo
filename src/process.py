import re
import json
import pandas as pd
import ollama
import time


MAX_TITLE_LENGTH = 53

SYSTEM_INSTRUCTIONS = f"""
You are an e-commerce SEO expert.
Rewrite the provided Shopify product title so it is concise, descriptive, SEO-friendly, and NO LONGER than {MAX_TITLE_LENGTH} characters.

OUTPUT RULES (very important):
- Output ONLY the rewritten title on a single line and nothing else. No explanation, no labels, no quotes, no code fences.
- If you cannot include the entire meaning, prioritize main product keywords (brand optional), not minor details such as size, color, or quantity.
- Do NOT end the title with meaningless or hanging words such as 'and', 'with', 'for', 'of', etc.
- Do NOT end the title with any punctuation or symbols like &, ,, ;, :, ., !, ?, etc.
- Ensure the title is complete, readable, and focuses on the most important product information.
"""

def extract_title_from_model_output(content: str) -> str:
    """
    Robust extraction:
      1. Try to parse JSON object if model returned JSON.
      2. Try to find quoted text.
      3. Take the last non-empty line and strip common prefixes.
      4. Fallback to first non-empty token sequence.
    """
    content = (content or "").strip()
    if not content:
        return ""

    # 1) JSON object attempt
    try:
        # find {...} in the text
        mjson = re.search(r'\{.*\}', content, flags=re.S)
        if mjson:
            obj = json.loads(mjson.group())
            # look for common keys
            for key in ("title", "new_title", "rewritten_title"):
                if key in obj and obj[key]:
                    return str(obj[key]).strip()
    except Exception:
        pass

    # 2) quoted substring like "Some title"
    m = re.search(r'["“”](.*?)["“”]', content)
    if m and m.group(1).strip():
        return m.group(1).strip()

    # 3) last non-empty line (after removing common labels)
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    if lines:
        last = lines[-1]
        # remove common prefix labels
        last = re.sub(
            r'^(New Title:|Title:|Rewritten Title:|Here\'s a rewritten title that is concise:)\s*',
            '',
            last,
            flags=re.I
        )
        last = last.strip(' "\'')
        if last:
            return last

    # 4) fallback: return the whole content condensed to one line
    single = " ".join(content.split())
    return single

def enforce_length(title: str) -> str:
    t = (title or "").strip()
    if len(t) <= MAX_TITLE_LENGTH:
        return t
    # Trim to the last whole word within the limit
    trimmed = t[:MAX_TITLE_LENGTH].rsplit(" ", 1)[0]
    # if trimming removed everything (very unlikely), hard cut
    if not trimmed:
        trimmed = t[:MAX_TITLE_LENGTH]
    return trimmed.strip()

def rewrite_title_llama(title: str, description: str) -> str:
    prompt = f"""Original Title: {title}
Product Description: {description}
New Title (<= {MAX_TITLE_LENGTH} chars):"""
    try:
        response = ollama.chat(
            model="gpt-oss:latest",
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": prompt}
            ])

        # Ollama returns something like {"message": {"content": "...."}}
        content = response.get("message", {}).get("content", "")
        extracted = extract_title_from_model_output(content)
        final_title = enforce_length(extracted)

        # Final safety: if extraction failed, fallback to original truncated
        if not final_title:
            final_title = enforce_length(title)

        return final_title

    except Exception as e:
        print(f"⚠️ Ollama error for title '{title}': {e}")
        # fallback: truncated original title
        return enforce_length(title)


def process_shopify_csv(input_file: str, output_file: str):
    df = pd.read_csv(input_file, dtype=str)

    if "Title" not in df.columns or "Body (HTML)" not in df.columns or "Status" not in df.columns:
        raise ValueError("CSV must contain 'Title', 'Body (HTML)', and 'Status' columns.")

    # Filter only active/draft products for progress tracking
    active_mask = df["Status"].str.strip().str.lower().isin(["active", "draft"])
    total_active = active_mask.sum()
    edited_count = 0
    start_time = time.time()

    print(f"🚀 Total active/draft products to process: {total_active}")

    def process_row(row):
        nonlocal edited_count

        status = str(row.get("Status", "")).strip().lower()
        title = row.get("SEO Title", "")
        desc = row.get("SEO Description", "")

        # Only process active/draft titles, skip others
        if status not in ("active") or pd.isna(title) or str(title).strip() == "":
            return title

        # Skip if already short enough
        if len(str(title)) <= MAX_TITLE_LENGTH:
            return title

        # Rewrite title
        new_t = rewrite_title_llama(str(title), str(desc))
        if new_t != title:
            edited_count += 1

        # Progress update
        active_processed_so_far = active_mask[:row.name+1].sum()
        remaining_active = total_active - active_processed_so_far
        elapsed = time.time() - start_time
        print(f"[Active {active_processed_so_far}/{total_active}] Edited: {edited_count} | "
              f"Remaining: {remaining_active} | Elapsed: {elapsed:.1f}s")
        print(f"Orig({len(title)}): {title}\n -> New({len(new_t)}): {new_t}\n")

        return new_t

    df["Edited Title"] = df.apply(process_row, axis=1)
    df.to_csv(output_file, index=False)

    total_time = time.time() - start_time
    print(f"✅ Processed file saved as: {output_file}")
    print(f"📝 Total active titles edited: {edited_count}")
    print(f"⏱ Total time taken: {total_time:.1f}s")


if __name__ == "__main__":
    input_csv = "/Users/joshuahellewell/Desktop/01-dev/shopify_app/data/products_export_1.csv"
    output_csv = "/Users/joshuahellewell/Desktop/01-dev/shopify_app/data/products_ai_local.csv"
    process_shopify_csv(input_csv, output_csv)
