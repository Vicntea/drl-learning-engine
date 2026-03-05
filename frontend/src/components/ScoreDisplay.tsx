import React, { useEffect, useRef } from "react";
import { Renderer, Stave, StaveNote, Voice, Formatter } from "vexflow";
import type { NoteData } from "../types/musicTypes";


interface ScoreDisplayProps {
  notes: NoteData[];
  timeSignature?: string;
  clef?: string;
}

const ScoreDisplay: React.FC<ScoreDisplayProps> = ({
  notes,
  timeSignature = "4/4",
  clef = "treble"
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || notes.length === 0) return;
    containerRef.current.innerHTML = "";

    try {
      const renderer = new Renderer(containerRef.current, Renderer.Backends.SVG);
      renderer.resize(800, 200);
      const context = renderer.getContext();

      // Configuración del compás
      const measureWidth = 300;
      let x = 10;
      const y = 40;
      const [beatsPerMeasure, beatValue] = timeSignature.split("/").map(Number);

      // Agrupar notas en compases
      const measures: NoteData[][] = [[]];
      let currentMeasure = 0;
      let currentBeats = 0;

      notes.forEach(note => {
        const duration = note.duration.replace(/[^whq0-9]/g, '');
        const durationValue = getDurationValue(duration);

        if (currentBeats + durationValue > beatsPerMeasure) {
          currentMeasure++;
          measures[currentMeasure] = [];
          currentBeats = 0;
        }

        measures[currentMeasure].push(note);
        currentBeats += durationValue;
      });

      // Renderizar cada compás
      measures.forEach((measure, index) => {
        const stave = new Stave(x, y, measureWidth);
        if (index === 0) {
          stave.addClef(clef).addTimeSignature(timeSignature);
        }
        stave.setContext(context).draw();
        const voice = new Voice({
            numBeats: beatsPerMeasure,
            beatValue: beatValue,
            });


        const staveNotes = measure.map(n => 
          new StaveNote({
            keys: n.keys,
            duration: n.duration,
          })
        );

        voice.addTickables(staveNotes);
        new Formatter().joinVoices([voice]).format([voice], measureWidth - 30);
        voice.draw(context, stave);

        x += measureWidth;
      });
    } catch (e) {
      console.error("Error al renderizar VexFlow:", e);
    }
  }, [notes, timeSignature, clef]);

  return (
    <div
      ref={containerRef}
      style={{ border: "1px solid gray", height: 200, overflow: "auto" }}
    />
  );
};

const getDurationValue = (duration: string): number => {
  const durationMap: { [key: string]: number } = {
    w: 4, h: 2, q: 1, "8": 0.5, "16": 0.25, "32": 0.125, "64": 0.0625
  };
  return durationMap[duration] || 1;
};

export default ScoreDisplay;
