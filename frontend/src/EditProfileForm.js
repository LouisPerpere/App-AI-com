import React, { useRef, useEffect } from 'react';
import StableTextInput from './StableTextInput';
import { Label } from './components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';

const EditProfileForm = ({ 
  editProfileForm, 
  onFieldChange, 
  businessTypes = []
}) => {
  const inputRefs = useRef({});

  // Create stable change handlers
  const handleFieldChange = (fieldName) => (value) => {
    onFieldChange(fieldName, value);
  };

  return (
    <div className="space-y-6">
      {/* Nom de l'entreprise */}
      <div className="space-y-2">
        <Label htmlFor="business_name_stable" className="text-sm font-medium text-gray-700">
          Nom de l'entreprise
        </Label>
        <StableTextInput
          ref={el => inputRefs.current.business_name = el}
          id="business_name_stable"
          value={editProfileForm.business_name}
          onChange={handleFieldChange('business_name')}
          placeholder="Nom de votre entreprise"
          required
        />
      </div>

      {/* Type d'entreprise */}
      <div className="space-y-2">
        <Label htmlFor="business_type" className="text-sm font-medium text-gray-700">
          Type d'entreprise
        </Label>
        <Select
          value={editProfileForm.business_type}
          onValueChange={handleFieldChange('business_type')}
        >
          <SelectTrigger>
            <SelectValue placeholder="Sélectionnez le type" />
          </SelectTrigger>
          <SelectContent>
            {businessTypes.map((type) => (
              <SelectItem key={type.value} value={type.value}>
                {type.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Description de l'activité */}
      <div className="space-y-2">
        <Label htmlFor="business_description_stable" className="text-sm font-medium text-gray-700">
          Décrivez votre activité
        </Label>
        <StableTextInput
          ref={el => inputRefs.current.business_description = el}
          id="business_description_stable"
          value={editProfileForm.business_description}
          onChange={handleFieldChange('business_description')}
          placeholder="Décrivez en quelques mots votre activité, vos services ou produits..."
          rows={3}
          required
        />
      </div>

      {/* Audience cible */}
      <div className="space-y-2">
        <Label htmlFor="target_audience_stable" className="text-sm font-medium text-gray-700">
          Audience cible
        </Label>
        <StableTextInput
          ref={el => inputRefs.current.target_audience = el}
          id="target_audience_stable"
          value={editProfileForm.target_audience}
          onChange={handleFieldChange('target_audience')}
          placeholder="Décrivez votre audience cible"
          rows={3}
          required
        />
      </div>

      {/* Ton de la marque */}
      <div className="space-y-2">
        <Label htmlFor="brand_tone" className="text-sm font-medium text-gray-700">
          Ton de la marque
        </Label>
        <Select
          value={editProfileForm.brand_tone}
          onValueChange={handleFieldChange('brand_tone')}
        >
          <SelectTrigger>
            <SelectValue placeholder="Choisissez le ton" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="friendly">Amical</SelectItem>
            <SelectItem value="professional">Professionnel</SelectItem>
            <SelectItem value="casual">Décontracté</SelectItem>
            <SelectItem value="elegant">Élégant</SelectItem>
            <SelectItem value="energetic">Énergique</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Fréquence de publication */}
      <div className="space-y-2">
        <Label htmlFor="posting_frequency" className="text-sm font-medium text-gray-700">
          Fréquence de publication
        </Label>
        <Select
          value={editProfileForm.posting_frequency}
          onValueChange={handleFieldChange('posting_frequency')}
        >
          <SelectTrigger>
            <SelectValue placeholder="Sélectionnez la fréquence" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="daily">Quotidien</SelectItem>
            <SelectItem value="3x_week">3 fois par semaine</SelectItem>
            <SelectItem value="weekly">Hebdomadaire</SelectItem>
            <SelectItem value="bi_weekly">Bi-hebdomadaire</SelectItem>
            <SelectItem value="monthly">Mensuel</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Plateformes préférées */}
      <div className="space-y-2">
        <Label className="text-sm font-medium text-gray-700">Plateformes préférées</Label>
        <div className="grid grid-cols-3 gap-4">
          {['Facebook', 'Instagram', 'LinkedIn'].map((platform) => (
            <label key={platform} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={editProfileForm.preferred_platforms?.includes(platform)}
                onChange={(e) => {
                  const current = editProfileForm.preferred_platforms || [];
                  const updated = e.target.checked 
                    ? [...current, platform]
                    : current.filter(p => p !== platform);
                  onFieldChange('preferred_platforms', updated);
                }}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{platform}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Budget marketing */}
      <div className="space-y-2">
        <Label htmlFor="budget_range_stable" className="text-sm font-medium text-gray-700">
          Budget marketing mensuel
        </Label>
        <StableTextInput
          ref={el => inputRefs.current.budget_range = el}
          id="budget_range_stable"
          value={editProfileForm.budget_range}
          onChange={handleFieldChange('budget_range')}
          placeholder="Ex: 500€, 1000-2000€, etc."
        />
      </div>

      {/* Email professionnel */}
      <div className="space-y-2">
        <Label htmlFor="email_stable" className="text-sm font-medium text-gray-700">
          Email professionnel
        </Label>
        <StableTextInput
          ref={el => inputRefs.current.email = el}
          id="email_stable"
          type="email"
          value={editProfileForm.email}
          onChange={handleFieldChange('email')}
          placeholder="contact@entreprise.com"
        />
      </div>

      {/* Site web */}
      <div className="space-y-2">
        <Label htmlFor="website_url_stable" className="text-sm font-medium text-gray-700">
          Site web
        </Label>
        <StableTextInput
          ref={el => inputRefs.current.website_url = el}
          id="website_url_stable"
          type="url"
          value={editProfileForm.website_url}
          onChange={handleFieldChange('website_url')}
          placeholder="https://votre-site.com"
        />
      </div>
    </div>
  );
};

export default EditProfileForm;