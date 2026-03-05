export interface NoteData {
    keys: string[];    // Array of notes in VexFlow format (e.g., ["c/4"])
    duration: string;  // Duration in VexFlow format (e.g., "q", "h", "8", "w")
}

export interface MidiEvent {
    time: number;
    note: string;
    duration: number;
}

export interface ExerciseData {
  node: string;
  type: 'teorico' | 'practico' | 'dictado';
  difficulty: number;
  exercise: string;
  expected_answer: string;
  presentation_format: 'text_input' | 'multiple_choice';
}

export interface ApiResponse {
  status: string;
  data: {
    exercise: ExerciseData;
    presentation: {
      midiData: string;
      notes: NoteData[];
      rhythmPattern: string[];
    };
  };
}
