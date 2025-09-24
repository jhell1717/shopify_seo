"""
Main processor class for Shopify SEO optimisation.
"""

import re
import json
import pandas as pd
import ollama
import time
import os
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from .config import Config


@dataclass
class ProcessingResult:
    """Result of processing a Shopify CSV file."""
    
    output_file: str
    total_products: int
    active_products: int
    edited_titles: int
    processing_time: float
    success: bool
    error_message: Optional[str] = None


class ShopifySEOProcessor:
    """
    Main processor class for optimizing Shopify product titles using AI.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the processor with configuration.
        
        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config()
        self._ensure_temp_dir()
        
        # System instructions for the AI model
        self.system_instructions = f"""
        You are an e-commerce SEO expert.
        Rewrite the provided Shopify product title so it is concise, descriptive, SEO-friendly, and NO LONGER than {self.config.max_title_length} characters.

        OUTPUT RULES (very important):
        - Output ONLY the rewritten title on a single line and nothing else. No explanation, no labels, no quotes, no code fences.
        - If you cannot include the entire meaning, prioritize main product keywords (brand optional), not minor details such as size, color, or quantity.
        - Do NOT end the title with meaningless or hanging words such as 'and', 'with', 'for', 'of', etc.
        - Do NOT end the title with any punctuation or symbols like &, ,, ;, :, ., !, ?, etc.
        - Ensure the title is complete, readable, and focuses on the most important product information.
        """
    
    def _ensure_temp_dir(self) -> None:
        """Ensure the temporary directory exists."""
        os.makedirs(self.config.temp_dir, exist_ok=True)
    
    def _extract_title_from_model_output(self, content: str) -> str:
        """
        Robust extraction of title from AI model output.
        
        Args:
            content: Raw content from the AI model
            
        Returns:
            Extracted and cleaned title
        """
        content = (content or "").strip()
        if not content:
            return ""

        # 1) JSON object attempt
        try:
            mjson = re.search(r'\{.*\}', content, flags=re.S)
            if mjson:
                obj = json.loads(mjson.group())
                for key in ("title", "new_title", "rewritten_title"):
                    if key in obj and obj[key]:
                        return str(obj[key]).strip()
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

        # 2) quoted substring like "Some title"
        m = re.search(r'["""](.*?)["""]', content)
        if m and m.group(1).strip():
            return m.group(1).strip()

        # 3) last non-empty line (after removing common labels)
        lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
        if lines:
            last = lines[-1]
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

    def _enforce_length(self, title: str) -> str:
        """
        Enforce maximum title length constraint.
        
        Args:
            title: Title to enforce length on
            
        Returns:
            Title truncated to maximum length if necessary
        """
        t = (title or "").strip()
        if len(t) <= self.config.max_title_length:
            return t
        
        # Trim to the last whole word within the limit
        trimmed = t[:self.config.max_title_length].rsplit(" ", 1)[0]
        
        # if trimming removed everything (very unlikely), hard cut
        if not trimmed:
            trimmed = t[:self.config.max_title_length]
        
        return trimmed.strip()

    def _rewrite_title(self, title: str, description: str) -> str:
        """
        Rewrite a product title using AI.
        
        Args:
            title: Original product title
            description: Product description
            
        Returns:
            Rewritten title
        """
        prompt = f"""Original Title: {title}
        Product Description: {description}
        New Title (<= {self.config.max_title_length} chars):"""
        
        try:
            response = ollama.chat(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": self.system_instructions},
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.get("message", {}).get("content", "")
            extracted = self._extract_title_from_model_output(content)
            final_title = self._enforce_length(extracted)

            # Final safety: if extraction failed, fallback to original truncated
            if not final_title:
                final_title = self._enforce_length(title)

            return final_title

        except Exception as e:
            print(f"⚠️ Ollama error for title '{title}': {e}")
            # fallback: truncated original title
            return self._enforce_length(title)

    def validate_csv(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate that the CSV file has the required columns.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            df = pd.read_csv(file_path, dtype=str, nrows=1)
            required_columns = ["Title", "Body (HTML)", "Status", "SEO Title", "SEO Description"]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error reading CSV file: {str(e)}"

    def process_csv(self, input_file: str, output_file: Optional[str] = None) -> ProcessingResult:
        """
        Process a Shopify CSV file to optimize product titles.
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file. If None, generates automatically.
            
        Returns:
            ProcessingResult object with processing statistics
        """
        start_time = time.time()
        
        try:
            # Validate input file
            is_valid, error_msg = self.validate_csv(input_file)
            if not is_valid:
                return ProcessingResult(
                    output_file="",
                    total_products=0,
                    active_products=0,
                    edited_titles=0,
                    processing_time=0,
                    success=False,
                    error_message=error_msg
                )
            
            # Read CSV
            df = pd.read_csv(input_file, dtype=str)
            total_products = len(df)
            
            # Generate output filename if not provided
            if output_file is None:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                output_file = os.path.join(
                    self.config.temp_dir,
                    f"{base_name}_optimized_{int(time.time())}.csv"
                )
            
            # Filter only active/draft products for progress tracking
            active_mask = df["Status"].str.strip().str.lower().isin(["active", "draft"])
            total_active = active_mask.sum()
            edited_count = 0

            print(f"🚀 Total products: {total_products}")
            print(f"🚀 Total active/draft products to process: {total_active}")

            def process_row(row):
                nonlocal edited_count

                status = str(row.get("Status", "")).strip().lower()
                title = row.get("SEO Title", "")
                desc = row.get("SEO Description", "")

                # Only process active titles, skip others
                if status not in ("active") or pd.isna(title) or str(title).strip() == "":
                    return title

                # Skip if already short enough
                if len(str(title)) <= self.config.max_title_length:
                    return title

                # Rewrite title
                new_t = self._rewrite_title(str(title), str(desc))
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

            processing_time = time.time() - start_time
            
            return ProcessingResult(
                output_file=output_file,
                total_products=total_products,
                active_products=total_active,
                edited_titles=edited_count,
                processing_time=processing_time,
                success=True
            )

        except Exception as e:
            processing_time = time.time() - start_time
            return ProcessingResult(
                output_file="",
                total_products=0,
                active_products=0,
                edited_titles=0,
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )
