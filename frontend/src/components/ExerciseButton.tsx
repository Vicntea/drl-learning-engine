import React, { useState } from 'react';
import Nodo1aScorePlayer from './Nodo1aScorePlayer';

const ExerciseButton: React.FC = () => {
  const [showExercise, setShowExercise] = useState(false);
  const [exerciseKey, setExerciseKey] = useState(0);

  const handleNewExercise = () => {
    setExerciseKey(prev => prev + 1);
    setShowExercise(true);
  };

  return (
    <div className="exercise-container">
      <button 
        onClick={handleNewExercise}
        className="exercise-button"
      >
        {showExercise ? 'Generar Nuevo Ejercicio' : 'Comenzar Ejercicio'}
      </button>

      {showExercise && (
        <div key={exerciseKey}>
          <Nodo1aScorePlayer />
        </div>
      )}
    </div>
  );
};

export default ExerciseButton;
