import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Button, 
  Paper,
  SelectChangeEvent,
  Container,
  CircularProgress
} from '@mui/material';
import CodeIcon from '@mui/icons-material/Code';

interface LandingPageProps {
  onStart: (language: string, topic: string, difficulty: string) => void;
  isLoading?: boolean;
}

const LandingPage: React.FC<LandingPageProps> = ({ onStart, isLoading = false }) => {
  const [language, setLanguage] = useState('cpp');
  const [topic, setTopic] = useState('arrays');
  const [difficulty, setDifficulty] = useState('medium');

  const handleLanguageChange = (event: SelectChangeEvent) => {
    setLanguage(event.target.value);
  };

  const handleTopicChange = (event: SelectChangeEvent) => {
    setTopic(event.target.value);
  };

  const handleDifficultyChange = (event: SelectChangeEvent) => {
    setDifficulty(event.target.value);
  };

  const handleStartCoding = () => {
    onStart(language, topic, difficulty);
  };

  return (
    <Container maxWidth="sm">
      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          mt: 8, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center' 
        }}
      >
        <CodeIcon color="primary" sx={{ fontSize: 60, mb: 2 }} />
        <Typography variant="h4" gutterBottom>
          Coding Platform
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" align="center" sx={{ mb: 4 }}>
          Select your preferences to start coding
        </Typography>
        
        <Box sx={{ width: '100%', mb: 3 }}>
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel id="language-label">Programming Language</InputLabel>
            <Select
              labelId="language-label"
              value={language}
              label="Programming Language"
              onChange={handleLanguageChange}
              disabled={isLoading}
            >
              <MenuItem value="cpp">C++</MenuItem>
              <MenuItem value="java">Java</MenuItem>
              <MenuItem value="python">Python</MenuItem>
              <MenuItem value="c">C</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel id="topic-label">Question Topic</InputLabel>
            <Select
              labelId="topic-label"
              value={topic}
              label="Question Topic"
              onChange={handleTopicChange}
              disabled={isLoading}
            >
              <MenuItem value="arrays">Arrays</MenuItem>
              <MenuItem value="strings">Strings</MenuItem>
              <MenuItem value="linkedlists">Linked Lists</MenuItem>
              <MenuItem value="trees">Trees</MenuItem>
              <MenuItem value="graphs">Graphs</MenuItem>
              <MenuItem value="dp">Dynamic Programming</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl fullWidth sx={{ mb: 4 }}>
            <InputLabel id="difficulty-label">Difficulty Level</InputLabel>
            <Select
              labelId="difficulty-label"
              value={difficulty}
              label="Difficulty Level"
              onChange={handleDifficultyChange}
              disabled={isLoading}
            >
              <MenuItem value="easy">Easy</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="hard">Hard</MenuItem>
            </Select>
          </FormControl>
          
          <Button 
            variant="contained" 
            size="large" 
            fullWidth
            onClick={handleStartCoding}
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={24} color="inherit" /> : null}
          >
            {isLoading ? "Generating Problem..." : "Start Coding"}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default LandingPage; 