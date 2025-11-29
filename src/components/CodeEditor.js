'use client'
import { useState } from 'react'
import Editor from '@monaco-editor/react'

export default function CodeEditor({ 
  value = '',
  onChange,
  language = 'javascript',
  height = '400px'
}) {
  const [code, setCode] = useState(value)

  const handleChange = (newValue) => {
    setCode(newValue)
    if (onChange) {
      onChange(newValue)
    }
  }

  return (
    <div className="github-card">
      <Editor
        height={height}
        language={language}
        value={code}
        onChange={handleChange}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
        }}
      />
    </div>
  )
}
