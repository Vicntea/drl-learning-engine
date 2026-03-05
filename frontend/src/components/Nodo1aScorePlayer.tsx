import React, { useState, useEffect } from "react";
import ScoreDisplay from "./ScoreDisplay";
import ScorePlayer from "./ScorePlayer";
import TheoreticalExercise from "./TheoreticalExercise";
import type { NoteData, ApiResponse, ExerciseData } from "../types/musicTypes";

const Nodo1aScorePlayer: React.FC = () => {
  const [notes, setNotes] = useState<NoteData[]>([]);
  const [exerciseData, setExerciseData] = useState<ExerciseData | null>(null);
  const [midiData, setMidiData] = useState<ArrayBuffer | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchExercise = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/exercise"); // ajusta el puerto si tu backend es FastAPI
        const contentType = res.headers.get("content-type");
        if (!contentType?.includes("application/json")) {
          throw new Error("La respuesta no es JSON");
        }

        const response: ApiResponse = await res.json();

        if (response.status === "success") {
          console.log("Respuesta del servidor:", response);
          const { data } = response;
          setExerciseData(data.exercise);

          if (data.presentation?.notes) setNotes(data.presentation.notes);

          if (data.presentation?.midiData) {
            const binary = atob(data.presentation.midiData);
            const bytes = new Uint8Array([...binary].map((c) => c.charCodeAt(0)));
            setMidiData(bytes.buffer);
          }
        } else {
          console.error("Error en la respuesta del servidor:", response);
        }
      } catch (err) {
        console.error("Error al cargar datos del ejercicio:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchExercise();
  }, []);

  if (loading) return <div>Cargando ejercicio...</div>;
  if (!exerciseData) return <div>No se pudo cargar el ejercicio.</div>;

  return (
    <div style={{ padding: 20 }}>
      <h2>🎵 Ejercicio Musical</h2>

      {exerciseData.type === "teorico" ? (
        <TheoreticalExercise exerciseData={exerciseData} />
      ) : (
        <>
          <ScoreDisplay notes={notes} />
          <ScorePlayer notes={notes} />
          {midiData && (
            <p style={{ fontSize: 12, color: "gray", marginTop: 10 }}>
              Archivo MIDI cargado ({midiData.byteLength} bytes)
            </p>
          )}
        </>
      )}
    </div>
  );
};

export default Nodo1aScorePlayer;
