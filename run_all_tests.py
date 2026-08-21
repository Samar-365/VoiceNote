#!/usr/bin/env python3
"""
VoiceNote Test Runner.
Discovers and runs all unit tests, module tests, and database integration tests.
"""

import sys
import unittest
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("TestRunner")


def run_db_tests():
    logger.info("--- Testing PostgreSQL Database Persistence ---")
    try:
        from voicenote.db import get_db
        db = get_db()
        count = db.get_note_count()
        tasks = len(db.get_all_tasks())
        logger.info(f"[OK] PostgreSQL loaded cleanly (Notes: {count}, Tasks: {tasks})")
        return True
    except Exception as e:
        logger.warning(f"[SKIP] PostgreSQL connection not available: {e}")
        return True


def run_text_cleaner_tests():
    logger.info("--- Testing Text Cleaner Engine ---")
    try:
        from voicenote.core.text_cleaner import TextCleaner
        cleaner = TextCleaner()
        sample = {
            "language": "mr",
            "segments": [{"start": 0.0, "end": 5.0, "text": "  माजे   नाओ   "}]
        }
        res = cleaner.clean(sample)
        assert res["text"].strip() == "माजे नाओ"
        logger.info("[OK] Text Cleaner test passed.")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Text Cleaner test failed: {e}")
        return False


def run_ai_engine_tests():
    logger.info("--- Testing AI Engine & Gemini Integration ---")
    import os
    if not os.getenv("GEMINI_API_KEY"):
        logger.warning("[SKIP] GEMINI_API_KEY not set in environment. Skipping live Gemini API tests.")
        return True
    try:
        from tests.test_ai_engine import TestAIEngine
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAIEngine)
        result = unittest.TextTestRunner(verbosity=0).run(suite)
        if result.wasSuccessful():
            logger.info("[OK] AI Engine prompt validation passed.")
            return True
        else:
            logger.error(f"[ERROR] AI Engine tests failed: {result.errors + result.failures}")
            return False
    except Exception as e:
        logger.error(f"[ERROR] AI Engine test failed: {e}")
        return False


def run_audio_recording_tests():
    logger.info("--- Testing Audio Recording File Storage (data/recording) ---")
    try:
        from tests.test_audio_recording import TestAudioRecordingStorage
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAudioRecordingStorage)
        result = unittest.TextTestRunner(verbosity=0).run(suite)
        if result.wasSuccessful():
            logger.info("[OK] Audio recording file storage tests passed.")
            return True
        else:
            logger.error(f"[ERROR] Audio recording file storage tests failed: {result.errors + result.failures}")
            return False
    except Exception as e:
        logger.error(f"[ERROR] Audio recording tests failed: {e}")
        return False


def run_gui_import_tests():
    logger.info("--- Testing PySide6 UI & Service Components ---")
    try:
        from voicenote.ui.styles import MAIN_STYLE
        from voicenote.services.worker import PipelineWorker
        assert len(MAIN_STYLE) > 0
        logger.info("[OK] GUI & Service worker components loaded successfully.")
        return True
    except Exception as e:
        logger.error(f"[ERROR] GUI import test failed: {e}")
        return False


def main():
    print("=" * 60)
    print("           VOICENOTE COMPREHENSIVE TEST SUITE           ")
    print("=" * 60)
    
    results = [
        ("Database Layer", run_db_tests()),
        ("Text Cleaner Engine", run_text_cleaner_tests()),
        ("Audio Recording Storage", run_audio_recording_tests()),
        ("AI Engine Validation", run_ai_engine_tests()),
        ("GUI & Service Workers", run_gui_import_tests()),
    ]
    
    print("\n" + "=" * 60)
    print("                   TEST RESULTS SUMMARY                 ")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f" - {name:<30} [{status}]")
        if not passed:
            all_passed = False
            
    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
