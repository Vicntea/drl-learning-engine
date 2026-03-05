import React, { useRef, useState, useCallback, useEffect } from "react";
import * as Tone from "tone";
import type { NoteData } from "../types/musicTypes";

interface ScorePlayerProps {
  notes: NoteData[];
  initialBpm?: number;
}

// Estructura interna para eventos de reproducción
interface PlaybackEvent {
  time: number;
  note: string;
  duration: number;
}

const ScorePlayer: React.FC<ScorePlayerProps> = ({ notes, initialBpm = 100 }) => {
  const synthRef = useRef<Tone.PolySynth<Tone.Synth>>(null);
  const partRef = useRef<Tone.Part<PlaybackEvent> | null>(null);

  const [bpm, setBpm] = useState<number>(initialBpm);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);

  const durationMap: Record<string, number> = {
    w: 4,
    h: 2,
    q: 1,
    "8": 0.5,
    "16": 0.25,
    "32": 0.125,
    "64": 0.0625,
    r: 0
  };

  // Inicializa el sintetizador y BPM
  useEffect(() => {
    if (!synthRef.current) {
      synthRef.current = new Tone.PolySynth(Tone.Synth).toDestination();
    }
    Tone.Transport.bpm.value = bpm;
  }, [bpm]);

  // Función para detener la reproducción
  const stopPlayback = useCallback(() => {
    if (partRef.current) {
      partRef.current.stop();
      partRef.current.dispose();
      partRef.current = null;
    }
    Tone.Transport.stop();
    setIsPlaying(false);
    setIsPaused(false);
  }, []);

  // Función principal de reproducción
  const playScore = useCallback(async () => {
    if (notes.length === 0) return;
    await Tone.start();

    if (isPaused) {
      Tone.Transport.start();
      setIsPlaying(true);
      setIsPaused(false);
      return;
    }

    stopPlayback();
    setIsPlaying(true);

    const beatDuration = 60 / bpm;

    const events: PlaybackEvent[] = notes.map((note, index) => {
      const baseDuration = note.duration.replace(/[^whq0-9]/g, "");
      const isRest = note.duration.includes("r");

      return {
        time: index * beatDuration,
        note: isRest ? "r" : note.keys[0].replace("/", "").toUpperCase(),
        duration: (durationMap[baseDuration] ?? 1) * beatDuration
      };
    });

    const part = new Tone.Part<PlaybackEvent>((time, value) => {
      if (value.note !== "r") {
        synthRef.current?.triggerAttackRelease(value.note, value.duration, time);
      }
    }, events).start(0);

    partRef.current = part;
    Tone.Transport.start();
  }, [notes, bpm, isPaused, stopPlayback]);

  // Renderizado de controles
  return (
    <div>
      <div style={{ marginTop: 10 }}>
        <label>
          BPM:
          <input
            type="number"
            value={bpm}
            onChange={(e) => setBpm(Number(e.target.value) || 100)}
            style={{ width: 60, marginLeft: 5 }}
            disabled={isPlaying}
            min={20}
            max={300}
          />
        </label>
      </div>

      <div style={{ marginTop: 10 }}>
        {!isPlaying && !isPaused && (
          <button onClick={playScore}>▶️ Reproducir</button>
        )}
        {isPlaying && (
          <button
            onClick={() => {
              Tone.Transport.pause();
              setIsPlaying(false);
              setIsPaused(true);
            }}
          >
            ⏸ Pausar
          </button>
        )}
        {(isPlaying || isPaused) && (
          <button onClick={stopPlayback} style={{ marginLeft: 10 }}>
            ⏹ Detener
          </button>
        )}
      </div>
    </div>
  );
};

export default ScorePlayer;
