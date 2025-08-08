import React, { useRef } from 'react';
import StableTextInput from './StableTextInput';
import { Label } from './components/ui/label';

const NoteForm = ({ 
  noteForm, 
  onFieldChange 
}) => {
  const inputRefs = useRef({});

  // Create stable change handlers
  const handleFieldChange = (fieldName) => (value) => {
    onFieldChange(fieldName, value);
  };

  const handlePriorityChange = (e) => {
    onFieldChange('priority', e.target.value);
  };

  return (
    <div className="space-y-4">
      {/* Titre de la note */}
      <div>
        <Label htmlFor="note_title_stable" className="text-gray-700 font-medium">
          Titre
        </Label>
        <StableTextInput
          ref={el => inputRefs.current.title = el}
          id="note_title_stable"
          value={noteForm.title}
          onChange={handleFieldChange('title')}
          placeholder="Ex: Nouvelle promotion, Événement spécial..."
          className="mt-1 border-indigo-200 focus:border-indigo-500 focus-visible:ring-indigo-200"
          required
        />
      </div>

      {/* Contenu de la note */}
      <div>
        <Label htmlFor="note_content_stable" className="text-gray-700 font-medium">
          Contenu
        </Label>
        <StableTextInput
          ref={el => inputRefs.current.content = el}
          id="note_content_stable"
          value={noteForm.content}
          onChange={handleFieldChange('content')}
          placeholder="Décrivez les détails importants que vous voulez voir apparaître dans vos posts..."
          rows={4}
          className="mt-1 border-indigo-200 focus:border-indigo-500 focus-visible:ring-indigo-200"
          required
        />
      </div>

      {/* Priorité */}
      <div>
        <Label htmlFor="note_priority_stable" className="text-gray-700 font-medium">
          Priorité
        </Label>
        <select
          id="note_priority_stable"
          value={noteForm.priority || 'normal'}
          onChange={handlePriorityChange}
          className="mt-1 w-full p-3 border border-indigo-200 rounded-lg focus:border-indigo-500 bg-white text-sm"
        >
          <option value="low">Faible</option>
          <option value="normal">Normale</option>
          <option value="high">Élevée</option>
          <option value="urgent">Urgente</option>
        </select>
      </div>
    </div>
  );
};

export default NoteForm;