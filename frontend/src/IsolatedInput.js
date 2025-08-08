import React, { memo } from 'react';

// Composant input isolé pour éviter les re-rendus qui ferment le clavier
const IsolatedInput = memo(({ 
  id, 
  value, 
  onChange, 
  placeholder, 
  type = "text", 
  required = false,
  className = "",
  rows = null 
}) => {
  const handleChange = (e) => {
    onChange(e.target.value);
  };

  const baseClasses = "flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50";
  
  if (rows) {
    return (
      <textarea
        id={id}
        value={value || ''}
        onChange={handleChange}
        placeholder={placeholder}
        rows={rows}
        required={required}
        className={`${baseClasses} min-h-[80px] resize-none ${className}`}
      />
    );
  }

  return (
    <input
      id={id}
      type={type}
      value={value || ''}
      onChange={handleChange}
      placeholder={placeholder}
      required={required}
      className={`${baseClasses} h-10 ${className}`}
    />
  );
});

IsolatedInput.displayName = 'IsolatedInput';

export default IsolatedInput;