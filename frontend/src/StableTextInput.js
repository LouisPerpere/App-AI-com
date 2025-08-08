import React, { useRef, useImperativeHandle, forwardRef, useEffect } from 'react';

// Composant input complètement isolé utilisant des refs pour éviter les re-rendus
const StableTextInput = forwardRef(({ 
  id, 
  value, 
  onChange, 
  placeholder, 
  type = "text", 
  required = false,
  rows = null,
  className = ""
}, ref) => {
  const inputRef = useRef(null);
  const lastValueRef = useRef(value);

  // Expose methods to parent via ref
  useImperativeHandle(ref, () => ({
    focus: () => inputRef.current?.focus(),
    blur: () => inputRef.current?.blur(),
    getValue: () => inputRef.current?.value || '',
    setValue: (newValue) => {
      if (inputRef.current) {
        inputRef.current.value = newValue || '';
        lastValueRef.current = newValue;
      }
    }
  }));

  // Initialize value on mount
  useEffect(() => {
    if (inputRef.current && value !== undefined) {
      inputRef.current.value = value || '';
      lastValueRef.current = value;
    }
  }, []);

  // Update value only if it changed externally
  useEffect(() => {
    if (inputRef.current && value !== lastValueRef.current) {
      inputRef.current.value = value || '';
      lastValueRef.current = value;
    }
  }, [value]);

  const handleChange = (e) => {
    const newValue = e.target.value;
    lastValueRef.current = newValue;
    if (onChange) {
      onChange(newValue);
    }
  };

  const baseClasses = "flex w-full rounded-md border border-input bg-white px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2";
  
  if (rows) {
    return (
      <textarea
        ref={inputRef}
        id={id}
        defaultValue={value || ''}
        onChange={handleChange}
        placeholder={placeholder}
        rows={rows}
        required={required}
        className={`${baseClasses} min-h-[80px] resize-none ${className}`}
        style={{ fontSize: '16px' }} // Prevents zoom on iOS
      />
    );
  }

  return (
    <input
      ref={inputRef}
      id={id}
      type={type}
      defaultValue={value || ''}
      onChange={handleChange}
      placeholder={placeholder}
      required={required}
      className={`${baseClasses} h-10 ${className}`}
      style={{ fontSize: '16px' }} // Prevents zoom on iOS
    />
  );
});

StableTextInput.displayName = 'StableTextInput';

export default StableTextInput;