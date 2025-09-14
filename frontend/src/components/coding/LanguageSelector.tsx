import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Box,
  Typography,
} from '@mui/material';
import { SupportedLanguage } from '../../types/coding';
import { SUPPORTED_LANGUAGES } from '../../constants/languages';

interface LanguageSelectorProps {
  value: SupportedLanguage;
  onChange: (language: SupportedLanguage) => void;
  disabled?: boolean;
  allowedLanguages?: SupportedLanguage[];
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  value,
  onChange,
  disabled = false,
  allowedLanguages,
}) => {
  const availableLanguages = allowedLanguages 
    ? SUPPORTED_LANGUAGES.filter(lang => allowedLanguages.includes(lang.id))
    : SUPPORTED_LANGUAGES;

  const handleChange = (event: SelectChangeEvent<string>) => {
    onChange(event.target.value as SupportedLanguage);
  };

  return (
    <FormControl size="small" sx={{ minWidth: 150 }}>
      <InputLabel id="language-selector-label">Language</InputLabel>
      <Select
        labelId="language-selector-label"
        id="language-selector"
        value={value}
        label="Language"
        onChange={handleChange}
        disabled={disabled}
      >
        {availableLanguages.map((language) => (
          <MenuItem key={language.id} value={language.id}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2">
                {language.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                (.{language.fileExtension})
              </Typography>
            </Box>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};