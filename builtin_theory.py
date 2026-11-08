"""
Built-in Screenwriting & Filmmaking Theory Knowledge Corpus
Includes foundational frameworks from Syd Field, Robert McKee, Blake Snyder,
John Truby, Christopher Vogler, and John Yorke with chapter references.
"""

from typing import List, Dict, Any

BUILTIN_THEORY_CORPUS: List[Dict[str, Any]] = [
    # 1. SYD FIELD - SCREENPLAY & THE THREE-ACT PARADIGM
    {
        "source": "Syd Field - Screenplay: The Foundations of Screenwriting",
        "page": 21,
        "chapter": "Chapter 1: The Paradigm & Three-Act Structure",
        "content": (
            "Syd Field's Screenplay Paradigm defines the classical Three-Act Structure: "
            "Act I: Setup (approx. Pages 1-30). Establishes the protagonist, dramatic premise, and status quo. "
            "Plot Point 1 (approx. Pages 25-27): An irreversible event or decision that hooks into the action and spins the story into Act II. "
            "Act II: Confrontation (approx. Pages 30-90). The protagonist encounters mounting obstacles and conflict pursuing their dramatic need. "
            "Midpoint (approx. Page 60): A major anchor at the center of the story that shifts the narrative direction or raises the stakes. "
            "Plot Point 2 (approx. Pages 85-90): The second major crisis or turning point that propels the story directly into Act III. "
            "Act III: Resolution (approx. Pages 90-120). Contains the definitive climax and denouement, answering the central dramatic question."
        )
    },
    {
        "source": "Syd Field - Screenplay: The Foundations of Screenwriting",
        "page": 58,
        "chapter": "Chapter 4: Character Creation & Dramatic Need",
        "content": (
            "Dramatic Need is what your main character wants to win, gain, get, or achieve during the course of the screenplay. "
            "Dramatic need drives the action forward. Every scene should either reveal character or advance the story toward or away from this goal."
        )
    },

    # 2. ROBERT MCKEE - STORY
    {
        "source": "Robert McKee - Story: Substance, Structure, Style and Principles",
        "page": 181,
        "chapter": "Chapter 8: The Inciting Incident",
        "content": (
            "Robert McKee defines the Inciting Incident as an event that radically upsets the balance of forces in the protagonist's life, "
            "arousing in them the conscious desire to restore that balance. It must either happen on screen within the first quarter of the story "
            "or prior to the story, propelling the protagonist into an active quest for an Object of Desire."
        )
    },
    {
        "source": "Robert McKee - Story: Substance, Structure, Style and Principles",
        "page": 233,
        "chapter": "Chapter 10: Scene Design & Turning Points",
        "content": (
            "A scene is a story event that turns the value charge of a character's life situation from positive to negative or negative to positive "
            "through conflict. If a scene does not produce a value turn (e.g., hope to despair, danger to safety, loyalty to betrayal), the scene is non-eventful and redundant. "
            "The Gap between expectation and result is where story energy and character revelation occur."
        )
    },
    {
        "source": "Robert McKee - Story: Substance, Structure, Style and Principles",
        "page": 375,
        "chapter": "Chapter 13: Character Transformation",
        "content": (
            "Characterization is the sum of all observable traits (appearance, mannerisms, occupation). "
            "True Character is revealed only in the moral choices a human being makes under pressure. "
            "A complete character arc requires the protagonist's core belief or flaw to be tested and transformed through difficult dilemmas."
        )
    },

    # 3. BLAKE SNYDER - SAVE THE CAT!
    {
        "source": "Blake Snyder - Save the Cat! The Last Book on Screenwriting",
        "page": 70,
        "chapter": "Chapter 4: The 15-Beat Sheet",
        "content": (
            "Blake Snyder's 15-Beat Structure calibrated for feature films: "
            "1. Opening Image (p. 1): Snapshot of the flawed status quo. "
            "2. Theme Stated (p. 5): Conversational statement of the moral lesson. "
            "3. Set-Up (pp. 1-10): Protagonist's world, flaws, and ticking clock. "
            "4. Catalyst (p. 12): Inciting disruption knocking the old world away. "
            "5. Debate (pp. 12-25): Hesitation or fear before entering the journey. "
            "6. Break into Two (p. 25): Proactive choice to enter the upside-down world of Act II. "
            "7. B Story (p. 30): The love interest, mentor, or relationship carrying the theme. "
            "8. Fun and Games (pp. 30-55): The promise of the premise and trailer moments. "
            "9. Midpoint (p. 55): False victory or false collapse; stakes raised. "
            "10. Bad Guys Close In (pp. 55-75): External pressure mounts while internal doubt fractures the team. "
            "11. All Is Lost (p. 75): Lowest point, 'whiff of death', total defeat of the old approach. "
            "12. Dark Night of the Soul (pp. 75-85): Mourning and realization of true internal need. "
            "13. Break into Three (p. 85): Synthesis of external goal and internal thematic truth. "
            "14. Finale (pp. 85-110): Five-step execution overcoming the antagonist. "
            "15. Final Image (p. 110): Visual proof of irreversible transformation."
        )
    },

    # 4. JOHN TRUBY - THE ANATOMY OF STORY
    {
        "source": "John Truby - The Anatomy of Story: 22 Steps to Becoming a Master Storyteller",
        "page": 269,
        "chapter": "Chapter 8: The Seven Key Story Steps",
        "content": (
            "John Truby's 7 Key Story Steps: "
            "1. Weakness and Need: The protagonist has a psychological flaw hurting themselves and a moral flaw hurting others. "
            "2. Desire: A specific, tangible external goal driving the narrative spine. "
            "3. Opponent: Competes for the exact same goal and targets the protagonist's fatal weakness. "
            "4. Plan: Strategies devised to overcome the opponent. "
            "5. Battle / Climax: The final confrontation testing which value system prevails. "
            "6. Self-Revelation: The blinding moment where the protagonist overcomes their self-deception and fulfills their moral need. "
            "7. New Equilibrium: Normalcy resumes at a higher moral/emotional state."
        )
    },

    # 5. CHRISTOPHER VOGLER - THE WRITER'S JOURNEY
    {
        "source": "Christopher Vogler - The Writer's Journey: Mythic Structure for Writers",
        "page": 81,
        "chapter": "Stages of the Hero's Journey",
        "content": (
            "The 12 Stages of the Mythic Hero's Journey: "
            "Ordinary World, Call to Adventure, Refusal of the Call, Meeting with the Mentor, "
            "Crossing the First Threshold, Tests/Allies/Enemies, Approach to the Inmost Cave, "
            "The Ordeal (confronting death), Reward (Seizing the Sword), The Road Back, "
            "Resurrection (final spiritual/physical test), and Return with the Elixir."
        )
    },

    # 6. JOHN YORKE - INTO THE WOODS
    {
        "source": "John Yorke - Into the Woods: A Five-Act Journey into Story",
        "page": 45,
        "chapter": "Chapter 2: Five-Act Structural Symmetry",
        "content": (
            "John Yorke demonstrates that dramatic story structure mirrors the dialectic: Thesis (Act 1), "
            "Antithesis (Act 2 & 4), Midpoint Core (Act 3), and Synthesis (Act 5). "
            "Story structure is fractal: each scene, sequence, and act reflects this three-part breathing cycle."
        )
    }
]

