# Tyger Tyger QA Runner Guide

The `qa_runner.py` tool allows developers and QA testers to run the game with specific configurations, ensuring consistent test conditions.

## Quick Start

Run the tool from the root directory:

```bash
python qa_runner.py
```

This starts the game normally but wrapped in the QA harness.

## Features

### 1. Character Archetypes

Pre-configure the player's skills and attributes to test specific paths (e.g., Skeptic vs. Believer content).

*   **Reason (Skeptic)**: High Logic, Skepticism, Research.
    ```bash
    python qa_runner.py --archetype reason
    ```
*   **Intuition (Believer)**: High Paranormal Sensitivity, Instinct.
    ```bash
    python qa_runner.py --archetype intuition
    ```
*   **Trauma (Haunted)**: Low Sanity, High Endurance/Survival.
    ```bash
    python qa_runner.py --archetype trauma
    ```

### 2. Debug Toggles

Manipulate game state for testing specific conditions.

*   **Godmode**: Automatically pass all skill checks with a massive success margin.
    ```bash
    python qa_runner.py --godmode
    ```
*   **Set Sanity**: Start with a specific Sanity level (0-100).
    ```bash
    python qa_runner.py --set-sanity 10
    ```
    *Useful for testing hallucinations and breakdowns.*

*   **Trigger Events**: Set event flags or trigger specific mechanics immediately.
    ```bash
    python qa_runner.py --trigger-event aurora_surge
    ```

### 3. Automated Logging

Generate detailed logs for analysis in `logs/qa/`.

*   **Check Logging**: Logs every skill check (Skill, DC, Roll, Outcome, Scene).
    ```bash
    python qa_runner.py --log-checks
    ```
    *   Output: `logs/qa/qa_check_log.json`
    *   Also logs Board State (Active Theories) after every step to `logs/qa/qa_board_log.json`.

*   **Parser Logging**: Logs raw input vs. parsed intent to verify command understanding.
    ```bash
    python qa_runner.py --log-parser
    ```
    *   Output: `logs/qa/qa_parser_log.json`

## Example Test Scenarios

### Scenario A: The Lucid Skeptic
Verify that high Logic characters can identify the planted evidence without falling for the paranormal bait.

```bash
python qa_runner.py --archetype reason --godmode --log-checks --start-scene crime_scene
```

### Scenario B: The Hallucinating Witness
Test how the game handles parser commands when Sanity is critical (hallucinated prompts, distorted text).

```bash
python qa_runner.py --set-sanity 5 --log-parser --start-scene mirror_hall
```

### Scenario C: Event Triggers
Verify that the "Aurora Surge" event correctly applies time and ambient effects.

```bash
python qa_runner.py --trigger-event aurora_surge
```
