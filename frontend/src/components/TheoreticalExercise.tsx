import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import type { ExerciseData } from '../types/musicTypes';

interface Props {
  exerciseData: ExerciseData;
}

const TheoreticalExercise: React.FC<Props> = ({ exerciseData }) => {
  const [answer, setAnswer] = useState<string>('');
  const [feedback, setFeedback] = useState<string>('');

  const handleSubmit = () => {
    if (answer.trim().toLowerCase() === exerciseData.expected_answer.trim().toLowerCase()) {
      setFeedback('¡Correcto!');
    } else {
      setFeedback('Incorrecto, intenta de nuevo');
    }
  };

  return (
    <div className="theoretical-exercise" style={{ marginTop: 20 }}>
      <div className="question" style={{ marginBottom: 15 }}>
        <ReactMarkdown>{exerciseData.exercise}</ReactMarkdown>
      </div>

      <div className="answer-section" style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
        <input
          type="text"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Escribe tu respuesta"
          style={{ flex: 1, padding: '5px 10px' }}
        />
        <button onClick={handleSubmit} style={{ padding: '5px 10px' }}>Enviar</button>
      </div>

      {feedback && (
        <div
          className={`feedback ${feedback === '¡Correcto!' ? 'correct' : 'incorrect'}`}
          style={{ color: feedback === '¡Correcto!' ? 'green' : 'red', fontWeight: 'bold' }}
        >
          {feedback}
        </div>
      )}
    </div>
  );
};

export default TheoreticalExercise;
