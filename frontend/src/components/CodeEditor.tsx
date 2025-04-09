import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import { Box, Button, Paper, Typography, Select, MenuItem, FormControl, InputLabel, SelectChangeEvent, IconButton, Toolbar, Tooltip } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SendIcon from '@mui/icons-material/Send';
import AlarmIcon from '@mui/icons-material/Alarm';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SettingsIcon from '@mui/icons-material/Settings';
import CodeIcon from '@mui/icons-material/Code';
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import FullscreenIcon from '@mui/icons-material/Fullscreen';

interface CodeEditorProps {
  initialCode: string;
  language: string;
  onRunCode: (code: string) => void;
  onSubmitCode: (code: string) => void;
  onLanguageChange?: (language: string) => void;
}

const LANGUAGE_OPTIONS = [
  { value: 'cpp', label: 'C++', defaultCode: '#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int minOperations(vector<int>& nums, int k) {\n        // Write your code here\n        return 0;\n    }\n};' },
  { value: 'java', label: 'Java', defaultCode: 'class Solution {\n    public int minOperations(int[] nums, int k) {\n        // Write your code here\n        return 0;\n    }\n}' },
  { value: 'python', label: 'Python', defaultCode: 'class Solution:\n    def minOperations(self, nums: List[int], k: int) -> int:\n        # Write your code here\n        pass' },
  { value: 'c', label: 'C', defaultCode: '#include <stdio.h>\n\nint minOperations(int* nums, int numsSize, int k) {\n    // Write your code here\n    return 0;\n}' },
];

const CodeEditor: React.FC<CodeEditorProps> = ({
  initialCode,
  language: initialLanguage,
  onRunCode,
  onSubmitCode,
  onLanguageChange,
}) => {
  const [language, setLanguage] = useState(initialLanguage);
  const [code, setCode] = useState(() => {
    const langOption = LANGUAGE_OPTIONS.find(option => option.value === initialLanguage);
    return initialCode || (langOption ? langOption.defaultCode : '');
  });

  const handleEditorChange = (value: string | undefined) => {
    if (value) {
      setCode(value);
    }
  };

  const handleLanguageChange = (event: SelectChangeEvent) => {
    const newLanguage = event.target.value;
    setLanguage(newLanguage);
    
    // Update code for the new language
    const langOption = LANGUAGE_OPTIONS.find(option => option.value === newLanguage);
    if (langOption) {
      setCode(langOption.defaultCode);
    }
    
    if (onLanguageChange) {
      onLanguageChange(newLanguage);
    }
  };

  const getMonacoLanguage = (lang: string) => {
    switch (lang) {
      case 'cpp': return 'cpp';
      case 'java': return 'java';
      case 'python': return 'python';
      case 'c': return 'c';
      default: return 'javascript';
    }
  };

  return (
    <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', p: 1, display: 'flex', alignItems: 'center' }}>
        <Typography sx={{ mr: 2 }}>Code</Typography>
        <FormControl size="small" sx={{ minWidth: 120, mr: 2 }}>
          <Select
            value={language}
            onChange={handleLanguageChange}
            displayEmpty
            variant="outlined"
            size="small"
          >
            {LANGUAGE_OPTIONS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <Box sx={{ flexGrow: 1 }} />
        <Tooltip title="Code editor settings">
          <IconButton size="small">
            <SettingsIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Show line numbers">
          <IconButton size="small">
            <FormatListNumberedIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Fullscreen">
          <IconButton size="small">
            <FullscreenIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      <Box sx={{ flexGrow: 1, position: 'relative' }}>
        <Editor
          height="100%"
          language={getMonacoLanguage(language)}
          value={code}
          theme="vs-dark"
          onChange={handleEditorChange}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
          }}
        />
      </Box>
      <Box sx={{ borderTop: 1, borderColor: 'divider', p: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="body2" color="text.secondary">
          Saved
        </Typography>
        <Box>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<PlayArrowIcon />}
            onClick={() => onRunCode(code)}
            sx={{ mr: 1 }}
          >
            Run
          </Button>
          <Button
            variant="contained"
            color="success"
            startIcon={<SendIcon />}
            onClick={() => onSubmitCode(code)}
          >
            Submit
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default CodeEditor; 