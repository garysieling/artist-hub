import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useSearchParams } from 'react-router-dom';
import { Camera, Clock, Image, Target, Video, Upload, Plus, X, Play, Pause, ChevronLeft, TrendingUp, BarChart3, Award, Calendar, Settings, RefreshCw, Check, AlertCircle, Palette, Trash2, Edit, Search, Download } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './App.css';

const API_URL = 'http://localhost:3001/api';

// Main App Component
export default function ArtistDevHub() {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSkills();
  }, []);

  const loadSkills = async () => {
    try {
      const response = await fetch(`${API_URL}/skills`);
      const data = await response.json();
      setSkills(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load skills:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="spinner"></div>
          <p className="loading-text">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/skills" element={<SkillsManager skills={skills} setSkills={setSkills} />} />
        <Route path="/warmup" element={<DrawingWarmup skills={skills} />} />
        <Route path="/critique" element={<CritiqueTool skills={skills} />} />
        <Route path="/photos" element={<PhotoFinder skills={skills} />} />
        <Route path="/video" element={<VideoExtractor />} />
        <Route path="/progress" element={<ProgressAnalytics skills={skills} />} />
        <Route path="/admin" element={<AdminPanel />} />
        <Route path="/paints" element={<PaintManager />} />
      </Routes>
    </div>
  );
}

// Dashboard Component
function Dashboard() {
  const navigate = useNavigate();
  const tools = [
    { id: 'critique', name: 'Artwork Critique', icon: Target, description: 'Get structured feedback on your work', color: 'purple' },
    { id: 'warmup', name: 'Drawing Warmup', icon: Clock, description: 'Timed reference practice sessions', color: 'blue' },
    { id: 'photos', name: 'Photo Finder', icon: Camera, description: 'Search and filter your photo collection', color: 'green' },
    { id: 'skills', name: 'Skills Manager', icon: Target, description: 'Track and develop artistic skills', color: 'orange' },
    { id: 'paints', name: 'Paint Manager', icon: Palette, description: 'Track your paints and pigments with RGB values', color: 'pink' },
    { id: 'video', name: 'Video Frame Extractor', icon: Video, description: 'Extract key frames from videos', color: 'red' },
    { id: 'progress', name: 'Progress & Analytics', icon: TrendingUp, description: 'Track your artistic development', color: 'teal' },
    { id: 'admin', name: 'Admin Panel', icon: Settings, description: 'Manage Google Photos sync and settings', color: 'gray' }
  ];

  return (
    <div className="container">
      <div className="dashboard-header">
        <h1 className="gradient-text">Artist Development Hub</h1>
        <p className="subtitle">Your toolkit for artistic growth</p>
      </div>

      <div className="tools-grid">
        {tools.map(tool => (
          <button key={tool.id} onClick={() => navigate(`/${tool.id}`)} className="tool-card">
            <div className={`tool-icon tool-icon-${tool.color}`}>
              <tool.icon size={24} />
            </div>
            <h3>{tool.name}</h3>
            <p>{tool.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}

// Skills Manager Component
function SkillsManager({ skills, setSkills }) {
  const navigate = useNavigate();
  const [newSkill, setNewSkill] = useState('');
  const [showAddSkill, setShowAddSkill] = useState(false);
  const [saving, setSaving] = useState(false);

  const addSkill = async () => {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSaving(true);
      try {
        const response = await fetch(`${API_URL}/skills`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ skill: newSkill.trim() })
        });
        const data = await response.json();
        if (data.success) {
          setSkills(data.skills);
          setNewSkill('');
          setShowAddSkill(false);
        }
      } catch (error) {
        console.error('Failed to add skill:', error);
        alert('Failed to add skill. Please try again.');
      }
      setSaving(false);
    }
  };

  const removeSkill = async (skillToRemove) => {
    if (window.confirm(`Remove "${skillToRemove}" from your skills?`)) {
      try {
        const response = await fetch(`${API_URL}/skills/${encodeURIComponent(skillToRemove)}`, {
          method: 'DELETE'
        });
        const data = await response.json();
        if (data.success) {
          setSkills(data.skills);
        }
      } catch (error) {
        console.error('Failed to remove skill:', error);
        alert('Failed to remove skill. Please try again.');
      }
    }
  };

  return (
    <div className="container">
      <button onClick={() => navigate('/')} className="back-button">
        <ChevronLeft size={20} />
        Back to Dashboard
      </button>

      <div className="card">
        <h2>Skills Manager</h2>
        
        <div className="info-box info-box-blue">
          <h3>AI Recommendations</h3>
          <p>Based on your recent practice, consider focusing on: <strong>Composition</strong> and <strong>Foreshortening with Value</strong></p>
        </div>

        <div className="skills-header">
          <h3>Your Skills ({skills.length})</h3>
          <button onClick={() => setShowAddSkill(!showAddSkill)} className="button button-purple">
            <Plus size={16} />
            Add Skill
          </button>
        </div>

        {showAddSkill && (
          <div className="add-skill-form">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !saving && addSkill()}
              placeholder="Enter new skill name..."
              disabled={saving}
              className="input"
            />
            <button onClick={addSkill} disabled={saving} className="button button-green">
              {saving ? 'Adding...' : 'Add'}
            </button>
            <button
              onClick={() => { setShowAddSkill(false); setNewSkill(''); }}
              disabled={saving}
              className="button button-gray"
            >
              Cancel
            </button>
          </div>
        )}

        <div className="skills-grid">
          {skills.map((skill, index) => (
            <div key={index} className="skill-item">
              <span>{skill}</span>
              <button onClick={() => removeSkill(skill)} className="icon-button">
                <X size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Drawing Warmup Component
function DrawingWarmup({ skills }) {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // Get state from URL or defaults
  const [step, setStepState] = useState(searchParams.get('step') || 'setup');
  const [duration, setDurationState] = useState(searchParams.get('duration') ? parseInt(searchParams.get('duration')) : null);
  const [selectedSkills, setSelectedSkillsState] = useState(
    searchParams.get('skills') ? searchParams.get('skills').split(',').filter(s => s) : []
  );
  const [currentImageIndex, setCurrentImageIndexState] = useState(
    searchParams.get('imageIndex') ? parseInt(searchParams.get('imageIndex')) : 0
  );
  const [sessionPlan, setSessionPlan] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isPaused, setIsPaused] = useState(searchParams.get('paused') === 'true');
  const [sessionImages, setSessionImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [totalPausedTime, setTotalPausedTime] = useState(0);
  const [pauseStartTime, setPauseStartTime] = useState(null);
  const [sessionStartTime] = useState(Date.now());

  // Photo filters state
  const [photoIndex, setPhotoIndex] = useState(null);
  const [filterSuggestions, setFilterSuggestions] = useState({
    subject_types: [],
    genders: [],
    lightings: [],
    skills: []
  });
  const [photoFilters, setPhotoFiltersState] = useState({
    subjectType: 'All',
    gender: 'All',
    lighting: 'All',
    skill: 'All Skills',
    photoCollection: 'My Photos'
  });
  const [isContinuousMode, setIsContinuousMode] = useState(false);
  const [continuousDuration, setContinuousDurationState] = useState(null);

  // Wrapper functions that update both state and URL
  const setStep = (newStep) => {
    setStepState(newStep);
    updateURL({ step: newStep });
  };

  const setDuration = (newDuration) => {
    setDurationState(newDuration);
    updateURL({ duration: newDuration });
  };

  const setSelectedSkills = (newSkills) => {
    setSelectedSkillsState(newSkills);
    updateURL({ skills: newSkills.join(',') });
  };

  const setCurrentImageIndex = (newIndex) => {
    setCurrentImageIndexState(newIndex);
    updateURL({ imageIndex: newIndex });
  };

  const setPhotoFilters = (newFilters) => {
    setPhotoFiltersState(newFilters);
  };

  const setContinuousDuration = (newDuration) => {
    setContinuousDurationState(newDuration);
  };

  // Helper to update URL params
  const updateURL = (updates) => {
    const params = new URLSearchParams(searchParams);
    Object.entries(updates).forEach(([key, value]) => {
      if (value === null || value === undefined || value === '') {
        params.delete(key);
      } else {
        params.set(key, value);
      }
    });
    setSearchParams(params, { replace: true });
  };

  // Load photo index and filter suggestions
  useEffect(() => {
    const loadPhotoIndexData = async () => {
      try {
        const [indexRes, suggestionsRes] = await Promise.all([
          fetch(`${API_URL}/photo-index`),
          fetch(`${API_URL}/photo-index/filter-suggestions`)
        ]);
        if (indexRes.ok) {
          const indexData = await indexRes.json();
          setPhotoIndex(indexData);
        }
        if (suggestionsRes.ok) {
          const suggestionsData = await suggestionsRes.json();
          setFilterSuggestions(suggestionsData);
        }
      } catch (error) {
        console.error('Failed to load photo index:', error);
      }
    };
    loadPhotoIndexData();
  }, []);

  const durationOptions = [
    { value: 5, label: '5 minutes', plan: [{ count: 10, duration: 30 }] },
    { value: 10, label: '10 minutes', plan: [{ count: 15, duration: 30 }, { count: 5, duration: 60 }] },
    { value: 15, label: '15 minutes', plan: [{ count: 10, duration: 30 }, { count: 4, duration: 60 }, { count: 2, duration: 180 }] },
    { value: 20, label: '20 minutes', plan: [{ count: 10, duration: 30 }, { count: 4, duration: 60 }, { count: 2, duration: 180 }, { count: 1, duration: 300 }] },
    { value: 30, label: '30 minutes', plan: [{ count: 10, duration: 30 }, { count: 5, duration: 60 }, { count: 3, duration: 300 }] },
    { value: 60, label: '60 minutes', plan: [{ count: 10, duration: 30 }, { count: 5, duration: 60 }, { count: 5, duration: 300 }, { count: 2, duration: 600 }] }
  ];

  const continuousOptions = [
    { value: 0.5, label: '30 seconds' },
    { value: 2, label: '2 minutes' },
    { value: 3, label: '3 minutes' },
    { value: 5, label: '5 minutes' }
  ];

  // Restore session from URL on mount
  useEffect(() => {
    const urlStep = searchParams.get('step');
    const urlDuration = searchParams.get('duration');

    // If we have a duration in URL, restore the session plan
    if (urlDuration && !sessionPlan) {
      const selected = durationOptions.find(opt => opt.value === parseInt(urlDuration));
      if (selected) {
        setSessionPlan(selected.plan);
      }
    }

    // If step is 'session', we need to reload images
    if (urlStep === 'session' && sessionImages.length === 0 && sessionPlan) {
      const loadSessionImages = async () => {
        setLoading(true);
        try {
          const totalCount = sessionPlan.reduce((sum, p) => sum + p.count, 0);
          const response = await fetch(`${API_URL}/images/warmup-session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count: totalCount, skills: selectedSkills })
          });
          const images = await response.json();
          setSessionImages(images);

          // Restore the timer for current image
          if (sessionPlan && currentImageIndex < totalCount) {
            let imagesSoFar = 0;
            for (let plan of sessionPlan) {
              if (currentImageIndex < imagesSoFar + plan.count) {
                setTimeRemaining(plan.duration);
                break;
              }
              imagesSoFar += plan.count;
            }
          }
        } catch (error) {
          console.error('Failed to restore session images:', error);
        }
        setLoading(false);
      };
      loadSessionImages();
    }
  }, [searchParams.get('step'), sessionPlan]);

  const toggleSkill = (skill) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter(s => s !== skill));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const confirmSetup = () => {
    if (isContinuousMode) {
      // For continuous mode, create a simple plan with just the duration
      // The actual image loading will be infinite
      setSessionPlan([{ count: 1, duration: Math.round(continuousDuration * 60) }]);
    } else {
      const selected = durationOptions.find(opt => opt.value === duration);
      setSessionPlan(selected.plan);
    }
    setStep('confirm');
  };

  const startSession = async () => {
    setLoading(true);
    try {
      // For continuous mode, start with a batch of images. For timed mode, load the full count
      const initialCount = isContinuousMode ? 10 : sessionPlan.reduce((sum, p) => sum + p.count, 0);
      const response = await fetch(`${API_URL}/images/warmup-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: initialCount, skills: selectedSkills })
      });
      const images = await response.json();
      setSessionImages(images);
      setStep('session');
      setCurrentImageIndex(0);
      setTimeRemaining(sessionPlan[0].duration);
    } catch (error) {
      console.error('Failed to load images:', error);
      alert('Failed to load images. Make sure the backend is running.');
    }
    setLoading(false);
  };

  useEffect(() => {
    if (step === 'session' && !isPaused && timeRemaining > 0) {
      const timer = setTimeout(() => setTimeRemaining(timeRemaining - 1), 1000);
      return () => clearTimeout(timer);
    } else if (step === 'session' && timeRemaining === 0) {
      const totalImages = sessionPlan.reduce((sum, p) => sum + p.count, 0);
      if (isContinuousMode) {
        // For continuous mode, always move to next image and reload if needed
        const nextIndex = currentImageIndex + 1;

        // Load more images when we're running low
        if (nextIndex >= sessionImages.length - 2) {
          fetch(`${API_URL}/images/warmup-session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count: 10, skills: selectedSkills })
          }).then(res => res.json()).then(newImages => {
            setSessionImages(prev => [...prev, ...newImages]);
          }).catch(err => console.error('Failed to load more images:', err));
        }

        setCurrentImageIndex(nextIndex);
        setTimeRemaining(sessionPlan[0].duration);
      } else {
        // For timed mode, end session when we've completed all images
        if (currentImageIndex + 1 < totalImages) {
          let imagesSoFar = 0;
          for (let plan of sessionPlan) {
            if (currentImageIndex < imagesSoFar + plan.count) {
              setTimeRemaining(plan.duration);
              break;
            }
            imagesSoFar += plan.count;
          }
          setCurrentImageIndex(currentImageIndex + 1);
        } else {
          setStep('complete');
        }
      }
    }
  }, [step, isPaused, timeRemaining, currentImageIndex, sessionPlan, isContinuousMode, sessionImages.length, selectedSkills]);

  useEffect(() => {
    if (step === 'complete') {
      const logSession = async () => {
        try {
          // Calculate actual practice time (excluding paused time)
          const totalSessionTime = Date.now() - sessionStartTime;
          let finalPausedTime = totalPausedTime;

          // If currently paused when session ends, add that pause duration
          if (pauseStartTime) {
            finalPausedTime += Date.now() - pauseStartTime;
          }

          const actualPracticeTimeMs = totalSessionTime - finalPausedTime;
          const actualPracticeMinutes = Math.round(actualPracticeTimeMs / 1000 / 60);

          const totalImages = sessionPlan.reduce((sum, p) => sum + p.count, 0);
          await fetch(`${API_URL}/sessions/log`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              type: 'warmup',
              duration: actualPracticeMinutes, // Use actual practice time, not planned duration
              skills: selectedSkills,
              imageCount: totalImages,
              completedAt: new Date().toISOString()
            })
          });
        } catch (error) {
          console.error('Failed to log session:', error);
        }
      };
      logSession();
    }
  }, [step]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (step === 'setup') {
    return (
      <div className="container">
        <button onClick={() => navigate('/')} className="back-button">
          <ChevronLeft size={20} />
          Back to Dashboard
        </button>

        <div className="card">
          <h2>Drawing Warmup Setup</h2>

          <div className="section">
            <h3 className="section-title">Select Duration</h3>
            <div className="duration-grid">
              {durationOptions.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setDuration(opt.value)}
                  className={`duration-option ${duration === opt.value ? 'selected' : ''}`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div className="section">
            <h3 className="section-title">Drawing Mode</h3>
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="mode"
                  checked={!isContinuousMode}
                  onChange={() => setIsContinuousMode(false)}
                />
                <span>Timed Session</span>
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="mode"
                  checked={isContinuousMode}
                  onChange={() => setIsContinuousMode(true)}
                />
                <span>Continuous Drawing</span>
              </label>
            </div>

            {isContinuousMode && (
              <div>
                <p className="section-subtitle">Select drawing duration for each image</p>
                <div className="duration-grid">
                  {continuousOptions.map(opt => (
                    <button
                      key={opt.value}
                      onClick={() => setContinuousDuration(opt.value)}
                      className={`duration-option ${continuousDuration === opt.value ? 'selected' : ''}`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="section">
            <h3 className="section-title">Photo Filters (Optional)</h3>
            <p className="section-subtitle">Filter reference images by attributes</p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: '500', marginBottom: '0.5rem' }}>Photo Collection</label>
                <select
                  value={photoFilters.photoCollection}
                  onChange={(e) => setPhotoFilters({...photoFilters, photoCollection: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem' }}
                >
                  <option>My Photos</option>
                  <option>Reference Photos</option>
                  <option>My Art</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: '500', marginBottom: '0.5rem' }}>Subject Type</label>
                <select
                  value={photoFilters.subjectType}
                  onChange={(e) => setPhotoFilters({...photoFilters, subjectType: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem' }}
                >
                  <option>All</option>
                  {filterSuggestions.subject_types?.map(type => (
                    <option key={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: '500', marginBottom: '0.5rem' }}>Gender</label>
                <select
                  value={photoFilters.gender}
                  onChange={(e) => setPhotoFilters({...photoFilters, gender: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem' }}
                >
                  <option>All</option>
                  {filterSuggestions.genders?.map(gender => (
                    <option key={gender}>{gender}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: '500', marginBottom: '0.5rem' }}>Lighting</label>
                <select
                  value={photoFilters.lighting}
                  onChange={(e) => setPhotoFilters({...photoFilters, lighting: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem' }}
                >
                  <option>All</option>
                  {filterSuggestions.lightings?.map(lighting => (
                    <option key={lighting}>{lighting}</option>
                  ))}
                </select>
              </div>

              <div style={{ gridColumn: '1 / -1' }}>
                <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: '500', marginBottom: '0.5rem' }}>Skill Focus</label>
                <select
                  value={photoFilters.skill}
                  onChange={(e) => setPhotoFilters({...photoFilters, skill: e.target.value})}
                  style={{ width: '100%', padding: '0.5rem' }}
                >
                  <option>All Skills</option>
                  {filterSuggestions.skills?.map(skill => (
                    <option key={skill}>{skill}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <button
            onClick={confirmSetup}
            disabled={!duration && !isContinuousMode}
            className="button button-blue full-width"
          >
            Continue
          </button>
        </div>
      </div>
    );
  }

  if (step === 'confirm') {
    const totalImages = sessionPlan.reduce((sum, p) => sum + p.count, 0);
    return (
      <div className="container">
        <button onClick={() => setStep('setup')} className="back-button">
          <ChevronLeft size={20} />
          Back
        </button>

        <div className="card">
          <h2>Confirm Your Session</h2>

          <div className="session-plan-box">
            <h3 className="section-title">Session Plan:</h3>
            <ul className="session-plan-list">
              {sessionPlan.map((plan, idx) => (
                <li key={idx}>
                  <span className="plan-count">{plan.count}×</span>
                  <span>{formatTime(plan.duration)} each</span>
                </li>
              ))}
            </ul>
            <div className="session-totals">
              <p><span className="label">Total images:</span> <strong>{totalImages}</strong></p>
              <p><span className="label">Total time:</span> <strong>{duration} minutes</strong></p>
            </div>
          </div>

          {selectedSkills.length > 0 && (
            <div className="selected-skills-box">
              <h3>Focusing on:</h3>
              <div className="skill-tags">
                {selectedSkills.map(skill => (
                  <span key={skill} className="skill-tag">{skill}</span>
                ))}
              </div>
            </div>
          )}

          <div className="button-group">
            <button onClick={() => setStep('setup')} disabled={loading} className="button button-gray">
              Modify
            </button>
            <button onClick={startSession} disabled={loading} className="button button-green">
              {loading ? 'Loading Images...' : 'Start Session'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'session') {
    const totalImages = sessionPlan.reduce((sum, p) => sum + p.count, 0);
    const progress = ((currentImageIndex + 1) / totalImages) * 100;
    const currentImage = sessionImages[currentImageIndex];

    return (
      <div className="session-screen">
        <div className="session-header">
          <div className="session-controls">
            <button onClick={() => {
              const newPausedState = !isPaused;
              if (newPausedState) {
                // Starting pause
                setPauseStartTime(Date.now());
              } else {
                // Ending pause
                if (pauseStartTime) {
                  const pauseDuration = Date.now() - pauseStartTime;
                  setTotalPausedTime(totalPausedTime + pauseDuration);
                  setPauseStartTime(null);
                }
              }
              setIsPaused(newPausedState);
              updateURL({ paused: newPausedState });
            }} className="control-button">
              {isPaused ? <Play size={20} /> : <Pause size={20} />}
            </button>
            <span className="timer">{formatTime(timeRemaining)}</span>
          </div>
          <div className="session-info">
            <span>Image {currentImageIndex + 1} of {isContinuousMode ? '∞' : totalImages}</span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={async () => {
                  if (currentImage) {
                    try {
                      await fetch(`${API_URL}/metadata/image/mark-drawn`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                          imagePath: currentImage.path,
                          mediums: []
                        })
                      });
                      alert(`✓ Image marked as drawn!`);
                    } catch (error) {
                      console.error('Error marking image as drawn:', error);
                    }
                  }
                }}
                className="button button-secondary"
                style={{ fontSize: '0.85rem', padding: '0.5rem 0.75rem' }}
              >
                ✓ Drew This
              </button>
              <button onClick={() => setStep('complete')} className="button button-red">
                End Session
              </button>
            </div>
          </div>
        </div>

        <div className="session-content">
          {currentImage ? (
            <div className="reference-image-container">
              <img
                src={`${API_URL}/images/file?path=${encodeURIComponent(currentImage.path)}`}
                alt="Reference"
                className={`reference-image ${isPaused ? 'paused' : ''}`}
              />
              {isPaused && (
                <div className="pause-overlay">
                  <Pause size={64} />
                  <p>Session Paused</p>
                </div>
              )}
            </div>
          ) : (
            <div className="image-placeholder">
              <Image size={64} />
            </div>
          )}
        </div>

        <div className="session-progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      </div>
    );
  }

  if (step === 'complete') {
    const totalImages = sessionPlan.reduce((sum, p) => sum + p.count, 0);
    return (
      <div className="container">
        <div className="card completion-card">
          <h2 className="completion-title">Session Complete!</h2>
          <p className="completion-text">
            You practiced with {totalImages} reference images over {duration} minutes
          </p>
          {selectedSkills.length > 0 && (
            <div className="completion-skills">
              <p className="label">Skills practiced:</p>
              <div className="skill-tags">
                {selectedSkills.map(skill => (
                  <span key={skill} className="skill-tag">{skill}</span>
                ))}
              </div>
            </div>
          )}
          <div className="button-group">
            <button
              onClick={() => {
                setStepState('setup');
                setDurationState(null);
                setSelectedSkillsState([]);
                setSessionPlan(null);
                setSessionImages([]);
                setCurrentImageIndexState(0);
                // Clear all URL params
                setSearchParams({}, { replace: true });
              }}
              className="button button-blue"
            >
              Start Another Session
            </button>
            <button onClick={() => navigate('/')} className="button button-gray">
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }
}

// Critique Tool Component
function CritiqueTool({ skills }) {
  const navigate = useNavigate();
  const [drawings, setDrawings] = useState([]);
  const [selectedDrawing, setSelectedDrawing] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [generatingCritique, setGeneratingCritique] = useState(false);
  const [comment, setComment] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [artMovements, setArtMovements] = useState([]);
  const [movementGuidance, setMovementGuidance] = useState(null);
  const [loadingMovement, setLoadingMovement] = useState(false);
  const [importingFromGoogle, setImportingFromGoogle] = useState(false);

  useEffect(() => {
    loadDrawings();
    loadArtMovements();
  }, []);

  const loadDrawings = async () => {
    try {
      const response = await fetch(`${API_URL}/drawings`);
      const data = await response.json();
      setDrawings(data);
    } catch (error) {
      console.error('Failed to load drawings:', error);
    }
  };

  const loadArtMovements = async () => {
    try {
      const response = await fetch(`${API_URL}/art-movements`);
      const data = await response.json();
      setArtMovements(data);
    } catch (error) {
      console.error('Failed to load art movements:', error);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    if (comment) {
      formData.append('comment', comment);
    }

    try {
      const response = await fetch(`${API_URL}/drawings/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (data.success) {
        await loadDrawings();
        setComment('');
        setSelectedDrawing(data.drawing);
      }
    } catch (error) {
      console.error('Failed to upload drawing:', error);
      alert('Failed to upload drawing. Please try again.');
    }
    setUploading(false);
  };

  const generateCritique = async (drawingId) => {
    setGeneratingCritique(true);
    try {
      const response = await fetch(`${API_URL}/critiques/ai`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ drawingId })
      });
      const data = await response.json();
      if (data.success) {
        await loadDrawings();
        const updated = drawings.find(d => d.id === drawingId);
        if (updated) {
          setSelectedDrawing({...updated, critique: data.critique});
        }
      }
    } catch (error) {
      console.error('Failed to generate critique:', error);
      alert('Failed to generate critique. Please try again.');
    }
    setGeneratingCritique(false);
  };

  const updateComment = async (drawingId, newComment) => {
    try {
      const response = await fetch(`${API_URL}/drawings/${drawingId}/comment`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: newComment })
      });
      const data = await response.json();
      if (data.success) {
        await loadDrawings();
      }
    } catch (error) {
      console.error('Failed to update comment:', error);
    }
  };

  const deleteDrawing = async (drawingId) => {
    if (!window.confirm('Are you sure you want to delete this drawing?')) return;

    try {
      await fetch(`${API_URL}/drawings/${drawingId}`, { method: 'DELETE' });
      await loadDrawings();
      if (selectedDrawing?.id === drawingId) {
        setSelectedDrawing(null);
      }
    } catch (error) {
      console.error('Failed to delete drawing:', error);
    }
  };

  const compareToMovement = async (movementName) => {
    if (!selectedDrawing) return;

    setLoadingMovement(true);
    setMovementGuidance(null);

    try {
      const response = await fetch(`${API_URL}/art-movements/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          drawingId: selectedDrawing.id,
          movementName: movementName
        })
      });
      const data = await response.json();
      if (data.success) {
        setMovementGuidance(data);
      }
    } catch (error) {
      console.error('Failed to compare to movement:', error);
      alert('Failed to generate movement comparison. Please try again.');
    }
    setLoadingMovement(false);
  };

  const openGooglePhotosPickerForDrawing = async () => {
    setImportingFromGoogle(true);
    try {
      // Create a picker session
      const response = await fetch(`${API_URL}/google-photos/picker/create-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (!response.ok) {
        alert(`Failed to create picker session: ${data.detail}`);
        setImportingFromGoogle(false);
        return;
      }

      const { session_id, picker_uri, polling_config } = data;

      // Open the picker in a new window
      const pickerWindow = window.open(picker_uri, 'GooglePhotosPicker', 'width=800,height=600');

      // Poll for completion
      const pollInterval = polling_config?.pollInterval || 2000; // Poll more frequently
      const maxPolls = 60; // Maximum 60 polls (2 minutes at 2s intervals)
      let pollCount = 0;

      const pollSession = async () => {
        try {
          pollCount++;
          console.log(`Polling session ${session_id}... (poll #${pollCount})`);
          const statusResponse = await fetch(`${API_URL}/google-photos/picker/session/${session_id}`);
          const statusData = await statusResponse.json();

          console.log('Picker session status:', statusData);
          console.log('Window closed?', pickerWindow ? pickerWindow.closed : 'null');

          if (statusData.media_items_set) {
            // User has finished selecting photos
            console.log('Photos selected! Fetching media items...');
            if (pickerWindow && !pickerWindow.closed) {
              pickerWindow.close();
            }

            // Fetch the selected media items
            const mediaResponse = await fetch(`${API_URL}/google-photos/picker/session/${session_id}/media-items`);
            const mediaData = await mediaResponse.json();

            console.log('Media items:', mediaData);

            if (mediaData.count > 0) {
              await importGooglePhotosAsDrawings(mediaData.media_items);
            } else {
              alert('No photos were selected.');
              setImportingFromGoogle(false);
            }
          } else if (pollCount >= maxPolls) {
            // Timeout after max polls
            console.log('Polling timeout - no photos selected');
            alert('Picker session timed out. Please try again.');
            setImportingFromGoogle(false);
          } else {
            // Continue polling regardless of window state
            // The picker window closes itself after "Done" is clicked, but the API
            // needs time to update the session status
            console.log(`Continuing to poll in ${pollInterval}ms...`);
            setTimeout(pollSession, pollInterval);
          }
        } catch (error) {
          console.error('Error polling picker session:', error);
          setImportingFromGoogle(false);
        }
      };

      // Start polling
      setTimeout(pollSession, pollInterval);

    } catch (error) {
      console.error('Failed to open Google Photos Picker:', error);
      alert('Failed to open Google Photos Picker');
      setImportingFromGoogle(false);
    }
  };

  const importGooglePhotosAsDrawings = async (mediaItems) => {
    try {
      const response = await fetch(`${API_URL}/google-photos/import-as-drawing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          media_items: mediaItems.map(item => ({
            id: item.id,
            baseUrl: item.mediaFile?.url || item.baseUrl,
            filename: item.filename
          }))
        })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        alert(`Successfully imported ${result.imported_count} photo(s) from Google Photos!`);
        await loadDrawings();
        // Select the first imported drawing
        if (result.drawings && result.drawings.length > 0) {
          setSelectedDrawing(result.drawings[0]);
        }
      } else {
        alert(`Import failed: ${result.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Failed to import photos:', error);
      alert('Failed to import photos from Google Photos');
    } finally {
      setImportingFromGoogle(false);
    }
  };

  const filteredDrawings = drawings.filter(d =>
    d.originalName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.comment.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="container container-wide">
      <button onClick={() => navigate('/')} className="back-button">
        <ChevronLeft size={20} />
        Back to Dashboard
      </button>

      <h2>AI Art Critique</h2>
      <p className="subtitle">Upload your artwork for AI-powered critique using Feldman's four-step method</p>

      <div className="critique-layout">
        <div className="critique-sidebar">
          <div className="card">
            <h3>Upload New Drawing</h3>
            <label className="upload-area-small">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="file-input"
                disabled={uploading}
              />
              <Upload size={32} />
              <p className="upload-text-small">{uploading ? 'Uploading...' : 'Choose image'}</p>
            </label>

            <button
              onClick={openGooglePhotosPickerForDrawing}
              className="button-secondary"
              disabled={importingFromGoogle}
              style={{ width: '100%', marginTop: '12px' }}
            >
              <Camera size={16} style={{ marginRight: '8px' }} />
              {importingFromGoogle ? 'Importing...' : 'Import from Google Photos'}
            </button>

            <div className="form-group">
              <label className="form-label">Comment/Notes (optional)</label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Add notes about this drawing..."
                className="textarea"
                rows={3}
              />
            </div>
          </div>

          <div className="card">
            <h3>Your Drawings ({drawings.length})</h3>
            <input
              type="text"
              placeholder="Search drawings..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input"
            />

            <div className="drawings-list">
              {filteredDrawings.map(drawing => (
                <div
                  key={drawing.id}
                  className={`drawing-item ${selectedDrawing?.id === drawing.id ? 'selected' : ''}`}
                  onClick={() => setSelectedDrawing(drawing)}
                >
                  <img
                    src={`${API_URL}/drawings/${drawing.id}/file`}
                    alt={drawing.originalName}
                    className="drawing-thumbnail"
                  />
                  <div className="drawing-info">
                    <p className="drawing-name">{drawing.originalName}</p>
                    <p className="drawing-date">{new Date(drawing.uploadedAt).toLocaleDateString()}</p>
                    {drawing.critique && <span className="critique-badge">✓ Critiqued</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="critique-main">
          {selectedDrawing ? (
            <div className="card">
              <div className="drawing-header">
                <div>
                  <h3>{selectedDrawing.originalName}</h3>
                  <p className="drawing-meta">
                    Uploaded {new Date(selectedDrawing.uploadedAt).toLocaleString()}
                  </p>
                </div>
                <button
                  onClick={() => deleteDrawing(selectedDrawing.id)}
                  className="button-icon button-danger"
                  title="Delete drawing"
                >
                  <X size={20} />
                </button>
              </div>

              <div className="drawing-display">
                <img
                  src={`${API_URL}/drawings/${selectedDrawing.id}/file`}
                  alt={selectedDrawing.originalName}
                  className="drawing-full"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Your Notes</label>
                <textarea
                  value={selectedDrawing.comment}
                  onChange={(e) => updateComment(selectedDrawing.id, e.target.value)}
                  placeholder="Add your notes and observations..."
                  className="textarea"
                  rows={3}
                />
              </div>

              {!selectedDrawing.critique ? (
                <button
                  onClick={() => generateCritique(selectedDrawing.id)}
                  disabled={generatingCritique}
                  className="button button-purple full-width"
                >
                  {generatingCritique ? 'Generating Critique...' : 'Generate AI Critique'}
                </button>
              ) : (
                <div className="critique-results">
                  <h3>AI Critique Results</h3>
                  <p className="critique-subtitle">Comprehensive AI-powered art analysis using computer vision</p>

                  <div className="critique-section critique-section-description">
                    <h4>Description</h4>
                    <div className="critique-text">
                      <ReactMarkdown>{selectedDrawing.critique.description}</ReactMarkdown>
                    </div>
                  </div>

                  <div className="critique-section critique-section-composition">
                    <h4>Composition Analysis</h4>
                    <div className="critique-text">
                      <ReactMarkdown>{selectedDrawing.critique.composition}</ReactMarkdown>
                    </div>
                  </div>

                  <div className="critique-section critique-section-mood">
                    <h4>Mood & Atmosphere</h4>
                    <div className="critique-text">
                      <ReactMarkdown>{selectedDrawing.critique.mood}</ReactMarkdown>
                    </div>
                  </div>

                  <div className="critique-section critique-section-analysis">
                    <h4>Design Elements Analysis</h4>
                    <div className="critique-text">
                      <ReactMarkdown>{selectedDrawing.critique.analysis}</ReactMarkdown>
                    </div>
                  </div>

                  <div className="critique-section critique-section-interpretation">
                    <h4>Interpretation</h4>
                    <div className="critique-text">
                      <ReactMarkdown>{selectedDrawing.critique.interpretation}</ReactMarkdown>
                    </div>
                  </div>

                  <div className="critique-section critique-section-judgment">
                    <h4>Evaluation & Recommendations</h4>
                    <div className="critique-text">
                      <ReactMarkdown>{selectedDrawing.critique.judgment}</ReactMarkdown>
                    </div>
                  </div>

                  <button
                    onClick={() => generateCritique(selectedDrawing.id)}
                    disabled={generatingCritique}
                    className="button button-outline full-width"
                  >
                    Regenerate Critique
                  </button>

                  <div className="movement-comparison-section">
                    <h3>Compare to Art Movements</h3>
                    <p className="movement-subtitle">Select a movement to get guidance on how to align your work with that aesthetic</p>

                    <div className="movement-buttons">
                      {artMovements.map(movement => (
                        <button
                          key={movement.name}
                          onClick={() => compareToMovement(movement.name)}
                          disabled={loadingMovement}
                          className="movement-button"
                          title={movement.description}
                        >
                          {movement.name}
                        </button>
                      ))}
                    </div>

                    {movementGuidance && (
                      <div className="movement-guidance">
                        <button
                          onClick={() => setMovementGuidance(null)}
                          className="movement-close"
                          title="Close guidance"
                        >
                          <X size={20} />
                        </button>
                        <h4>{movementGuidance.movement} Guidance</h4>
                        <div className="movement-guidance-text">
                          <ReactMarkdown>{movementGuidance.guidance}</ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="card empty-state">
              <Upload size={64} className="empty-icon" />
              <h3>No Drawing Selected</h3>
              <p>Upload a new drawing or select one from your collection to view and critique</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Photo Finder Component
function PhotoFinder({ skills }) {
  const navigate = useNavigate();
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [photoMetadata, setPhotoMetadata] = useState({});
  const [selectedMediums, setSelectedMediums] = useState([]);
  const [indexStatus, setIndexStatus] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  // Google Photos importer states
  const [showImageImporter, setShowImageImporter] = useState(false);
  const [imageImportStep, setImageImportStep] = useState('category'); // 'category', 'picker', 'syncing'
  const [importCategory, setImportCategory] = useState(null); // 'reference', 'artwork', 'warmup'
  const [pickerSessionId, setPickerSessionId] = useState(null);
  const [syncProgress, setSyncProgress] = useState(null);

  // Filter states
  const [filters, setFilters] = useState({
    subjectType: 'All',
    gender: 'All',
    lighting: 'All',
    status: 'All',
    skill: 'All Skills'
  });

  // Photo category filter (My Photos, Reference Photos, Historical Art, My Art)
  const [photoCategory, setPhotoCategory] = useState('Reference Photos');

  // Image attribute analysis (for debugging indexer)
  const [analyzedAttributes, setAnalyzedAttributes] = useState({});
  const [analyzingImage, setAnalyzingImage] = useState(false);

  // Photo index and AI-generated metadata
  const [photoIndex, setPhotoIndex] = useState(null);
  const [filterSuggestions, setFilterSuggestions] = useState({
    subject_types: [],
    genders: [],
    lightings: [],
    skills: []
  });

  // Shopping cart states
  const [cartImages, setCartImages] = useState([]);
  const [view, setView] = useState('browse'); // 'browse' or 'paint'

  // Painting session states
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [sessionStartTime, setSessionStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [imageTimes, setImageTimes] = useState({});
  const [isPainting, setIsPainting] = useState(false);

  // Seeded random number generator (for day-based consistency)
  const seededRandom = (seed) => {
    const x = Math.sin(seed++) * 10000;
    return x - Math.floor(x);
  };

  const getDaySeed = () => {
    const today = new Date();
    return today.getFullYear() * 10000 + (today.getMonth() + 1) * 100 + today.getDate();
  };

  const shuffleArrayWithSeed = (array, seed) => {
    const shuffled = [...array];
    let currentSeed = seed;

    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(seededRandom(currentSeed) * (i + 1));
      currentSeed++;
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }

    return shuffled;
  };

  const checkIndexStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/images/index-status`);
      const data = await response.json();
      setIndexStatus(data);
    } catch (error) {
      console.error('Failed to check index status:', error);
    }
  };

  const buildSearchQuery = () => {
    let parts = [];

    // Add search query
    if (searchQuery.trim()) {
      parts.push(searchQuery.trim());
    }

    // Add filters to query
    if (filters.subjectType !== 'All') {
      parts.push(filters.subjectType.toLowerCase());
    }
    if (filters.gender !== 'All') {
      parts.push(filters.gender.toLowerCase());
    }
    if (filters.lighting !== 'All') {
      parts.push(filters.lighting.toLowerCase() + ' lighting');
    }
    if (filters.skill !== 'All Skills') {
      parts.push('good for practicing ' + filters.skill.toLowerCase());
    }

    return parts.join(', ');
  };

  const loadPhotos = async (useSearch = false) => {
    setLoading(true);
    setIsSearching(useSearch);

    try {
      const metadataResponse = await fetch(`${API_URL}/metadata`);
      const metadataData = await metadataResponse.json();
      setPhotoMetadata(metadataData.images || {});

      let photosData;

      // Use AI search if query or filters are active
      const hasQuery = searchQuery.trim() ||
                       filters.subjectType !== 'All' ||
                       filters.gender !== 'All' ||
                       filters.lighting !== 'All' ||
                       filters.skill !== 'All Skills';

      if (useSearch && hasQuery) {
        const query = buildSearchQuery();
        console.log('Searching with query:', query);

        const searchResponse = await fetch(`${API_URL}/images/search`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: query,
            filters: filters,
            max_results: 100
          })
        });

        const searchData = await searchResponse.json();
        photosData = searchData.results || [];
      } else {
        // Load photos based on category
        if (photoCategory === 'My Photos') {
          const photosResponse = await fetch(`${API_URL}/images/photos`);
          photosData = await photosResponse.json();
        } else if (photoCategory === 'Reference Photos') {
          const refResponse = await fetch(`${API_URL}/images/reference`);
          photosData = await refResponse.json();
        } else if (photoCategory === 'My Art') {
          const artworkResponse = await fetch(`${API_URL}/drawings`);
          photosData = await artworkResponse.json();
        } else if (photoCategory === 'Historical Art') {
          // No results yet - placeholder for future implementation
          photosData = [];
        }

        // Shuffle photos randomly on each load
        photosData = photosData.sort(() => Math.random() - 0.5);
      }

      // Apply status filter client-side
      if (filters.status !== 'All') {
        photosData = photosData.filter(photo => {
          const metadata = metadataData.images?.[photo.path];
          if (filters.status === 'Already Drawn') {
            return metadata?.drawn === true;
          } else if (filters.status === 'Not Drawn') {
            return !metadata?.drawn;
          }
          return true;
        });

        // If showing "Already Drawn", sort by most recently drawn first
        if (filters.status === 'Already Drawn') {
          photosData.sort((a, b) => {
            const drawnAtA = metadataData.images?.[a.path]?.drawnAt;
            const drawnAtB = metadataData.images?.[b.path]?.drawnAt;

            // Both have timestamps - sort by most recent first
            if (drawnAtA && drawnAtB) {
              return new Date(drawnAtB) - new Date(drawnAtA);
            }
            // One has timestamp, put it first
            if (drawnAtA) return -1;
            if (drawnAtB) return 1;
            // Neither has timestamp
            return 0;
          });
        }
      }

      // Apply AI-indexed metadata filters (subject type, gender, lighting, skill)
      if (photoIndex && photoIndex.collections) {
        const collectionName =
          photoCategory === 'My Photos' ? 'My Photos' :
          photoCategory === 'Reference Photos' ? 'Reference Photos' :
          photoCategory === 'My Art' ? 'My Art' :
          'My Photos';

        const indexedMetadata = photoIndex.collections[collectionName] || {};

        photosData = photosData.filter(photo => {
          // Normalize path for lookup - convert absolute path to relative path
          let lookupPath = photo.path;

          // Extract just the relative part after the last directory separator that matters
          // From: D:\projects\art-models\googlephotos\all\vacation2025\file.jpg
          // To: all\vacation2025\file.jpg
          const pathParts = photo.path.split('\\');
          if (pathParts.length > 0) {
            // Find if this is from "googlephotos" (My Photos), reference, or artwork directories
            if (photoCategory === 'My Photos' || photoCategory === 'My Photos') {
              // For My Photos, look for "all" directory and use everything from there
              const allIndex = pathParts.findIndex(p => p.toLowerCase() === 'all');
              if (allIndex !== -1) {
                lookupPath = pathParts.slice(allIndex).join('\\');
              }
            } else if (photoCategory === 'Reference Photos') {
              // For Reference Photos, try to find the relative portion
              const refIndex = pathParts.findIndex(p =>
                p.match(/^\d+$/) || // numeric directory like 4, 5, 8
                p.toLowerCase().includes('reference')
              );
              if (refIndex !== -1) {
                lookupPath = pathParts.slice(refIndex + 1).join('\\');
              }
            }
          }

          const indexed = indexedMetadata[lookupPath] || indexedMetadata[photo.path];

          // If no indexed metadata, show the photo (fallback)
          if (!indexed) return true;

          // Apply subject type filter
          if (filters.subjectType !== 'All' && indexed.subject_type !== filters.subjectType) {
            return false;
          }

          // Apply gender filter
          if (filters.gender !== 'All' && indexed.gender !== filters.gender) {
            return false;
          }

          // Apply lighting filter
          if (filters.lighting !== 'All' && indexed.lighting !== filters.lighting) {
            return false;
          }

          // Apply skill filter
          if (filters.skill !== 'All Skills' &&
              (!indexed.skills || !indexed.skills.includes(filters.skill))) {
            return false;
          }

          return true;
        });
      }

      setPhotos(photosData);
    } catch (error) {
      console.error('Failed to load photos:', error);
    }
    setLoading(false);
    setIsSearching(false);
  };

  const toggleMedium = (medium) => {
    if (selectedMediums.includes(medium)) {
      setSelectedMediums(selectedMediums.filter(m => m !== medium));
    } else {
      setSelectedMediums([...selectedMediums, medium]);
    }
  };

  const markAsDrawn = async () => {
    if (!selectedPhoto) return;

    const newMetadata = {
      drawn: true,
      mediums: selectedMediums,
      drawnAt: new Date().toISOString()
    };

    try {
      await fetch(`${API_URL}/metadata/image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          imagePath: selectedPhoto.path,
          metadata: newMetadata
        })
      });

      // Update local state
      setPhotoMetadata({
        ...photoMetadata,
        [selectedPhoto.path]: {
          ...photoMetadata[selectedPhoto.path],
          ...newMetadata
        }
      });

      setSelectedPhoto(null);
      setSelectedMediums([]);
    } catch (error) {
      console.error('Failed to mark as drawn:', error);
      alert('Failed to save. Please try again.');
    }
  };

  const markAsNotDrawn = async () => {
    if (!selectedPhoto) return;

    try {
      await fetch(`${API_URL}/metadata/image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          imagePath: selectedPhoto.path,
          metadata: { drawn: false, mediums: [], drawnAt: null }
        })
      });

      // Update local state
      setPhotoMetadata({
        ...photoMetadata,
        [selectedPhoto.path]: {
          ...photoMetadata[selectedPhoto.path],
          drawn: false,
          mediums: [],
          drawnAt: null
        }
      });

      setSelectedPhoto(null);
      setSelectedMediums([]);
    } catch (error) {
      console.error('Failed to mark as not drawn:', error);
      alert('Failed to save. Please try again.');
    }
  };

  const analyzeImageAttributes = async (photo) => {
    setAnalyzingImage(true);
    try {
      const response = await fetch(`${API_URL}/photo-index/analyze-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imagePath: photo.path })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('Analysis response:', data);

      if (data.success) {
        setAnalyzedAttributes({
          ...analyzedAttributes,
          [photo.path]: {
            subject_type: data.subject_type,
            gender: data.gender,
            lighting: data.lighting,
            skills: data.skills
          }
        });
      } else if (data.error) {
        throw new Error(data.error);
      } else {
        throw new Error(data.message || 'Unknown error');
      }
    } catch (error) {
      console.error('Failed to analyze image:', error);
      alert(`Error: ${error.message}`);
    }
    setAnalyzingImage(false);
  };

  const openPhotoModal = (photo) => {
    setSelectedPhoto(photo);
    const metadata = photoMetadata[photo.path];
    setSelectedMediums(metadata?.mediums || []);
  };

  // Shopping Cart Functions
  const toggleCartImage = (photo) => {
    const isInCart = cartImages.some(img => img.path === photo.path);
    if (isInCart) {
      setCartImages(cartImages.filter(img => img.path !== photo.path));
    } else {
      setCartImages([...cartImages, photo]);
    }
  };

  const isImageInCart = (photo) => {
    return cartImages.some(img => img.path === photo.path);
  };

  const startPaintingSession = () => {
    if (cartImages.length === 0) {
      alert('Please add images to your cart first');
      return;
    }
    setCurrentImageIndex(0);
    setSessionStartTime(Date.now());
    setElapsedTime(0);
    setImageTimes({});
    setIsPainting(true);
    setView('paint');
  };

  const switchToImage = (index) => {
    if (imageTimes[currentImageIndex] === undefined && currentImageIndex < cartImages.length) {
      setImageTimes({
        ...imageTimes,
        [currentImageIndex]: elapsedTime
      });
    }
    setCurrentImageIndex(index);
  };

  const endPaintingSession = async () => {
    // Record final time for current image
    if (imageTimes[currentImageIndex] === undefined) {
      setImageTimes({
        ...imageTimes,
        [currentImageIndex]: elapsedTime
      });
    }

    // Log the session to backend
    try {
      await fetch(`${API_URL}/sessions/log`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'painting',
          duration: Math.round(elapsedTime / 60),
          imageCount: cartImages.length,
          imageTimes: imageTimes,
          completedAt: new Date().toISOString()
        })
      });
    } catch (error) {
      console.error('Failed to log painting session:', error);
    }

    setView('browse');
    setIsPainting(false);
    setCartImages([]);
    setCurrentImageIndex(0);
    setSessionStartTime(null);
    setElapsedTime(0);
    setImageTimes({});
  };

  // Timer effect for painting session
  useEffect(() => {
    if (!isPainting || !sessionStartTime) return;

    const interval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - sessionStartTime) / 1000));
    }, 100);

    return () => clearInterval(interval);
  }, [isPainting, sessionStartTime]);

  // Google Photos Importer Functions
  const startImageImport = () => {
    setShowImageImporter(true);
    setImageImportStep('category');
  };

  const selectCategory = async (category) => {
    setImportCategory(category);
    setImageImportStep('picker');

    // Create a picker session
    try {
      const response = await fetch(`${API_URL}/google-photos/picker/create-session`, {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setPickerSessionId(data.session_id);
        // Open picker in a new window
        if (data.picker_uri) {
          window.open(data.picker_uri, 'picker', 'width=600,height=800');
        }
      } else {
        alert('Failed to start picker. Please make sure you\'re authorized.');
      }
    } catch (error) {
      console.error('Error creating picker session:', error);
      alert('Failed to start picker');
    }
  };

  const completeImageImport = async () => {
    if (!pickerSessionId) {
      console.error('No picker session ID available');
      alert('Error: No picker session. Please try again.');
      return;
    }

    setImageImportStep('syncing');
    setSyncProgress({ total: 0, current: 0, status: 'Importing images...' });

    try {
      console.log(`Starting import for session: ${pickerSessionId}, category: ${importCategory}`);

      const response = await fetch(`${API_URL}/google-photos/picker/import-to-category`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: pickerSessionId,
          category: importCategory
        })
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Import successful:', data);
        setSyncProgress({
          total: data.total,
          current: data.imported,
          status: 'Import complete!'
        });

        // Reset after 2 seconds
        setTimeout(() => {
          setShowImageImporter(false);
          setImageImportStep('category');
          setSyncProgress(null);
          setPickerSessionId(null);
          loadPhotos(); // Reload photos to show newly imported ones
        }, 2000);
      } else {
        console.error('Import failed:', data);
        alert(`Failed to import images: ${data.detail || 'Unknown error'}`);
        setImageImportStep('picker');
      }
    } catch (error) {
      console.error('Error importing images:', error);
      alert(`Failed to import images: ${error.message}`);
      setImageImportStep('picker');
    }
  };

  const closeImageImporter = () => {
    setShowImageImporter(false);
    setImageImportStep('category');
    setSyncProgress(null);
    setPickerSessionId(null);
  };

  useEffect(() => {
    loadPhotos();
    checkIndexStatus();
  }, []);

  // Reload photos when photo category changes
  useEffect(() => {
    loadPhotos(false);
  }, [photoCategory]);

  // Reload photos when filters change
  useEffect(() => {
    // Only reload if photos are already loaded (to avoid loading twice on mount)
    if (photos.length > 0) {
      loadPhotos(false);
    }
  }, [filters.subjectType, filters.gender, filters.lighting, filters.skill, filters.status]);

  // Load photo index and filter suggestions on component mount
  useEffect(() => {
    const loadPhotoIndexData = async () => {
      try {
        // Load the photo index
        const indexResponse = await fetch(`${API_URL}/photo-index`);
        if (indexResponse.ok) {
          const index = await indexResponse.json();
          setPhotoIndex(index);
        }

        // Load filter suggestions
        const suggestionsResponse = await fetch(`${API_URL}/photo-index/filter-suggestions`);
        if (suggestionsResponse.ok) {
          const suggestions = await suggestionsResponse.json();
          setFilterSuggestions(suggestions);
        }
      } catch (error) {
        console.error('Error loading photo index data:', error);
      }
    };

    loadPhotoIndexData();
  }, []);

  if (view === 'paint' && isPainting) {
    // Painting session view
    const currentImage = cartImages[currentImageIndex];
    const formatTime = (seconds) => {
      const hours = Math.floor(seconds / 3600);
      const mins = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;
      if (hours > 0) {
        return `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
      }
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
      <div className="container container-wide">
        <button onClick={() => navigate('/')} className="back-button">
          <ChevronLeft size={20} />
          Back to Dashboard
        </button>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <h2>Painting Session</h2>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
                {formatTime(elapsedTime)}
              </div>
              <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
                {currentImageIndex + 1} / {cartImages.length}
              </p>
            </div>
          </div>

          {currentImage && (
            <div>
              <div style={{ position: 'relative', marginBottom: '2rem' }}>
                <img
                  src={`${API_URL}/images/file?path=${encodeURIComponent(currentImage.path)}`}
                  alt="Current reference"
                  style={{
                    width: '100%',
                    maxHeight: '60vh',
                    objectFit: 'contain',
                    borderRadius: '8px',
                    backgroundColor: '#f0f0f0'
                  }}
                />
              </div>

              {/* Carousel of images below */}
              <div style={{ marginBottom: '2rem' }}>
                <div style={{
                  display: 'flex',
                  gap: '1rem',
                  overflowX: 'auto',
                  paddingBottom: '1rem',
                  borderTop: '1px solid #eee',
                  paddingTop: '1rem'
                }}>
                  {cartImages.map((img, idx) => (
                    <button
                      key={idx}
                      onClick={() => switchToImage(idx)}
                      style={{
                        flexShrink: 0,
                        width: '120px',
                        height: '120px',
                        padding: idx === currentImageIndex ? '3px' : '0',
                        border: idx === currentImageIndex ? '3px solid #667eea' : 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        backgroundColor: 'transparent',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      <img
                        src={`${API_URL}/images/file?path=${encodeURIComponent(img.path)}`}
                        alt={`Reference ${idx + 1}`}
                        style={{
                          width: '100%',
                          height: '100%',
                          objectFit: 'cover',
                          borderRadius: '5px',
                          opacity: idx === currentImageIndex ? 1 : 0.6
                        }}
                      />
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                <button
                  onClick={() => {
                    if (currentImageIndex > 0) {
                      switchToImage(currentImageIndex - 1);
                    }
                  }}
                  disabled={currentImageIndex === 0}
                  className="button button-secondary"
                >
                  ← Previous
                </button>
                <button
                  onClick={endPaintingSession}
                  className="button button-red"
                >
                  End Session
                </button>
                <button
                  onClick={() => {
                    if (currentImageIndex < cartImages.length - 1) {
                      switchToImage(currentImageIndex + 1);
                    }
                  }}
                  disabled={currentImageIndex === cartImages.length - 1}
                  className="button button-secondary"
                >
                  Next →
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Browse view
  return (
    <div className="container container-wide">
      <button onClick={() => navigate('/')} className="back-button">
        <ChevronLeft size={20} />
        Back to Dashboard
      </button>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h2>Photo Finder</h2>
          {cartImages.length > 0 && (
            <button
              onClick={startPaintingSession}
              className="button button-blue"
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              <Play size={20} />
              Start Painting ({cartImages.length})
            </button>
          )}
        </div>

        {showImageImporter && (
          <div className="modal-overlay">
            <div className="modal">
              <button
                onClick={closeImageImporter}
                className="modal-close"
              >
                <X size={24} />
              </button>

              {imageImportStep === 'category' && (
                <div className="album-importer">
                  <h3>Add Images from Google Photos</h3>
                  <p className="section-subtitle">Where do you want to save these images?</p>

                  <div className="category-buttons">
                    <button
                      onClick={() => selectCategory('reference')}
                      className="category-btn"
                    >
                      <Image size={32} />
                      <span>Reference Images</span>
                      <p>Reference images for studies</p>
                    </button>
                    <button
                      onClick={() => selectCategory('artwork')}
                      className="category-btn"
                    >
                      <Upload size={32} />
                      <span>Artwork</span>
                      <p>Your own artwork pieces</p>
                    </button>
                    <button
                      onClick={() => selectCategory('warmup')}
                      className="category-btn"
                    >
                      <Clock size={32} />
                      <span>Warmup Images</span>
                      <p>Quick sketches and warmups</p>
                    </button>
                  </div>
                </div>
              )}

              {imageImportStep === 'picker' && (
                <div className="album-importer">
                  <h3>Select Images</h3>
                  <p className="section-subtitle">Choose images from Google Photos</p>

                  <div style={{
                    backgroundColor: '#f5f5f5',
                    padding: '2rem',
                    borderRadius: '8px',
                    textAlign: 'center',
                    marginBottom: '1rem'
                  }}>
                    <p style={{ marginBottom: '1rem' }}>A Google Photos picker window should have opened.</p>
                    <p style={{ color: '#666', fontSize: '0.9rem' }}>
                      If it didn't appear, you may need to check your browser's popup blocker.
                      <br />
                      Please select your images in the picker window, then click "Done" when finished.
                    </p>
                    <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: '#999' }}>
                      Session ID: {pickerSessionId?.substring(0, 8)}...
                    </p>
                  </div>

                  <div className="button-group">
                    <button
                      onClick={() => setImageImportStep('category')}
                      className="button button-secondary"
                    >
                      Back
                    </button>
                    <button
                      onClick={completeImageImport}
                      className="button button-primary"
                    >
                      Complete Import
                    </button>
                  </div>
                </div>
              )}

              {imageImportStep === 'syncing' && syncProgress && (
                <div className="album-importer">
                  <h3>Importing...</h3>
                  <div className="sync-progress">
                    <div className="spinner"></div>
                    <p>{syncProgress.status}</p>
                    {syncProgress.total > 0 && (
                      <p className="progress-text">
                        {syncProgress.current} / {syncProgress.total} images imported
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <button
            onClick={startImageImport}
            className="button button-primary"
          >
            <Download size={20} style={{ marginRight: '0.5rem' }} />
            Add Images from Google Photos
          </button>

          <div style={{ flex: 1, position: 'relative' }}>
            <input
              type="file"
              accept=".zip"
              onChange={async (e) => {
                const file = e.target.files?.[0];
                if (!file) return;

                const formData = new FormData();
                formData.append('zip_file', file);
                formData.append('category', 'reference');

                try {
                  const response = await fetch(`${API_URL}/images/upload-zip`, {
                    method: 'POST',
                    body: formData
                  });

                  if (response.ok) {
                    const data = await response.json();
                    alert(`Successfully imported ${data.imported} images!`);
                    loadPhotos();
                  } else {
                    const error = await response.json();
                    alert(`Failed to import: ${error.detail}`);
                  }
                } catch (error) {
                  console.error('Error uploading zip:', error);
                  alert(`Error uploading file: ${error.message}`);
                }

                // Reset input
                e.target.value = '';
              }}
              style={{ display: 'none' }}
              id="zip-upload-input"
            />
            <label
              htmlFor="zip-upload-input"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.5rem',
                backgroundColor: '#e3f2fd',
                color: '#1976d2',
                border: '2px dashed #1976d2',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                fontWeight: '500'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#bbdefb';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#e3f2fd';
              }}
            >
              <Upload size={20} />
              Upload ZIP of Images
            </label>
          </div>
        </div>

        {indexStatus && !indexStatus.indexed && (
          <div className="alert alert-info">
            <p>⚡ AI search is not yet configured. Building image index for the first time...</p>
            <button
              onClick={async () => {
                const response = await fetch(`${API_URL}/images/rebuild-index`, { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                  checkIndexStatus();
                  alert('Index built successfully! You can now use AI search.');
                }
              }}
              className="button button-small"
            >
              Build Index Now
            </button>
          </div>
        )}

        <div className="search-section">
          <input
            type="text"
            placeholder="Search for photos using AI (e.g., 'person jumping', 'sunset over water')..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && loadPhotos(true)}
            className="input search-input"
          />
          <button
            onClick={() => loadPhotos(true)}
            disabled={isSearching}
            className="button button-primary search-button"
          >
            {isSearching ? 'Searching...' : 'AI Search'}
          </button>
        </div>

        <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">Photo Collection</label>
            <select
              className="select-input"
              value={photoCategory}
              onChange={(e) => setPhotoCategory(e.target.value)}
            >
              <option>My Photos</option>
              <option>Reference Photos</option>
              <option>Historical Art</option>
              <option>My Art</option>
            </select>
          </div>
          <div className="filter-group">
            <label className="filter-label">Subject Type</label>
            <select
              className="select-input"
              value={filters.subjectType}
              onChange={(e) => setFilters({...filters, subjectType: e.target.value})}
            >
              <option>All</option>
              {filterSuggestions.subject_types && filterSuggestions.subject_types
                .filter(type => type !== 'All')
                .map(type => (
                  <option key={type}>{type}</option>
                ))}
            </select>
          </div>
          <div className="filter-group">
            <label className="filter-label">Gender</label>
            <select
              className="select-input"
              value={filters.gender}
              onChange={(e) => setFilters({...filters, gender: e.target.value})}
            >
              <option>All</option>
              {filterSuggestions.genders && filterSuggestions.genders
                .filter(gender => gender !== 'All')
                .map(gender => (
                  <option key={gender}>{gender}</option>
                ))}
            </select>
          </div>
          <div className="filter-group">
            <label className="filter-label">Lighting</label>
            <select
              className="select-input"
              value={filters.lighting}
              onChange={(e) => setFilters({...filters, lighting: e.target.value})}
            >
              <option>All</option>
              {filterSuggestions.lightings && filterSuggestions.lightings
                .filter(lighting => lighting !== 'All')
                .map(lighting => (
                  <option key={lighting}>{lighting}</option>
                ))}
            </select>
          </div>
          <div className="filter-group">
            <label className="filter-label">Status</label>
            <select
              className="select-input"
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
            >
              <option>All</option>
              <option>Not Drawn</option>
              <option>Already Drawn</option>
            </select>
          </div>
          <div className="filter-group">
            <label className="filter-label">Skills</label>
            <select
              className="select-input"
              value={filters.skill}
              onChange={(e) => setFilters({...filters, skill: e.target.value})}
            >
              <option>All Skills</option>
              {/* Use AI-indexed skills if available, fallback to manual skills list */}
              {(filterSuggestions.skills && filterSuggestions.skills.length > 0
                ? filterSuggestions.skills
                : skills
              ).map(skill => (
                <option key={skill}>{skill}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="search-actions">
          <button
            onClick={() => {
              setSearchQuery('');
              setPhotoCategory('Reference Photos');
              setFilters({
                subjectType: 'All',
                gender: 'All',
                lighting: 'All',
                status: 'All',
                skill: 'All Skills'
              });
              loadPhotos(false);
            }}
            className="button button-secondary"
          >
            Clear Filters
          </button>
        </div>

        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading photos...</p>
          </div>
        ) : photos.length > 0 ? (
          <div>
            <p className="photo-count">Found {photos.length} photos</p>
            <div className="photo-grid">
              {photos.slice(0, 50).map((photo, idx) => {
                const metadata = photoMetadata[photo.path];
                const isDrawn = metadata?.drawn === true;
                const inCart = isImageInCart(photo);

                return (
                  <div
                    key={idx}
                    style={{ position: 'relative', group: 'photo' }}
                    onMouseEnter={(e) => {
                      const checkbox = e.currentTarget.querySelector('.cart-checkbox');
                      if (checkbox) checkbox.style.opacity = '1';
                    }}
                    onMouseLeave={(e) => {
                      const checkbox = e.currentTarget.querySelector('.cart-checkbox');
                      if (checkbox && !inCart) checkbox.style.opacity = '0';
                    }}
                  >
                    <div
                      className={`photo-card ${isDrawn ? 'photo-drawn' : ''}`}
                      onClick={() => openPhotoModal(photo)}
                    >
                      <img
                        src={`${API_URL}/images/file?path=${encodeURIComponent(photo.path)}`}
                        alt={photo.name}
                        className="photo-thumbnail"
                      />
                      {isDrawn && (
                        <div className="photo-drawn-badge">
                          ✓ Drawn
                        </div>
                      )}
                      <div className="photo-info">
                        <p className="photo-name">{photo.name}</p>
                        {metadata?.mediums && metadata.mediums.length > 0 && (
                          <p className="photo-mediums">{metadata.mediums.join(', ')}</p>
                        )}
                      </div>
                    </div>

                    {/* Hover Checkbox for Shopping Cart */}
                    <button
                      className="cart-checkbox"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleCartImage(photo);
                      }}
                      style={{
                        position: 'absolute',
                        top: '10px',
                        right: '10px',
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        border: '2px solid white',
                        backgroundColor: inCart ? '#667eea' : 'rgba(0, 0, 0, 0.5)',
                        color: 'white',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '24px',
                        opacity: inCart ? '1' : '0',
                        transition: 'all 0.3s ease',
                        zIndex: 10,
                        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
                        padding: '0'
                      }}
                    >
                      {inCart ? '✓' : '+'}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <Camera size={64} />
            <p>No photos found</p>
            <p className="empty-subtext">Check that your photos directory is configured correctly</p>
          </div>
        )}
      </div>

      {/* Photo Modal */}
      {selectedPhoto && (
        <div className="modal-overlay" onClick={() => setSelectedPhoto(null)}>
          <div className="modal-content photo-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedPhoto(null)}>
              <X size={24} />
            </button>

            <div className="modal-body">
              <div className="modal-image-container">
                <img
                  src={`${API_URL}/images/file?path=${encodeURIComponent(selectedPhoto.path)}`}
                  alt={selectedPhoto.name}
                  className="modal-image"
                />
              </div>

              <div className="modal-sidebar">
                <h3>{selectedPhoto.name}</h3>

                {photoMetadata[selectedPhoto.path]?.drawn ? (
                  <div>
                    <div className="drawn-status">
                      <span className="status-badge status-badge-green">✓ Drawn</span>
                      {photoMetadata[selectedPhoto.path]?.drawnAt && (
                        <p className="status-date">
                          {new Date(photoMetadata[selectedPhoto.path].drawnAt).toLocaleDateString()}
                        </p>
                      )}
                    </div>

                    {photoMetadata[selectedPhoto.path]?.mediums && photoMetadata[selectedPhoto.path].mediums.length > 0 && (
                      <div className="mediums-display">
                        <h4>Mediums Used:</h4>
                        <div className="medium-tags">
                          {photoMetadata[selectedPhoto.path].mediums.map(medium => (
                            <span key={medium} className="medium-tag">{medium}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    <button onClick={markAsNotDrawn} className="button button-gray full-width">
                      Mark as Not Drawn
                    </button>
                  </div>
                ) : (
                  <div>
                    <h4>Mark as Drawn</h4>
                    <p className="section-subtitle">Select medium(s) used:</p>

                    <div className="medium-checkboxes">
                      {['Pen and Ink', 'Pencil', 'Watercolor', 'Print'].map(medium => (
                        <label key={medium} className="checkbox-label">
                          <input
                            type="checkbox"
                            checked={selectedMediums.includes(medium)}
                            onChange={() => toggleMedium(medium)}
                          />
                          {medium}
                        </label>
                      ))}
                    </div>

                    <button
                      onClick={markAsDrawn}
                      disabled={selectedMediums.length === 0}
                      className="button button-green full-width"
                    >
                      Mark as Drawn
                    </button>
                  </div>
                )}

                {/* Image Attributes Section (for debugging indexer) */}
                <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid #e0e0e0' }}>
                  <h4>AI Analysis (Debug)</h4>
                  <p className="section-subtitle">Analyze image attributes with indexer</p>

                  <button
                    onClick={() => analyzeImageAttributes(selectedPhoto)}
                    disabled={analyzingImage}
                    className="button button-secondary full-width"
                    style={{ marginBottom: '1rem' }}
                  >
                    {analyzingImage ? 'Analyzing...' : 'Analyze Attributes'}
                  </button>

                  {analyzedAttributes[selectedPhoto.path] && (
                    <div style={{ marginTop: '1rem' }}>
                      <div style={{ marginBottom: '0.75rem' }}>
                        <strong>Subject Type:</strong>
                        <p style={{ color: '#666', marginTop: '0.25rem' }}>{analyzedAttributes[selectedPhoto.path].subject_type}</p>
                      </div>
                      <div style={{ marginBottom: '0.75rem' }}>
                        <strong>Gender:</strong>
                        <p style={{ color: '#666', marginTop: '0.25rem' }}>{analyzedAttributes[selectedPhoto.path].gender}</p>
                      </div>
                      <div style={{ marginBottom: '0.75rem' }}>
                        <strong>Lighting:</strong>
                        <p style={{ color: '#666', marginTop: '0.25rem' }}>{analyzedAttributes[selectedPhoto.path].lighting}</p>
                      </div>
                      <div>
                        <strong>Skills:</strong>
                        <div style={{ marginTop: '0.25rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                          {analyzedAttributes[selectedPhoto.path].skills.map(skill => (
                            <span key={skill} style={{ backgroundColor: '#f0f0f0', padding: '0.25rem 0.75rem', borderRadius: '4px', fontSize: '0.85rem' }}>
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Video Extractor Component
function VideoExtractor() {
  const navigate = useNavigate();
  const [videoPath, setVideoPath] = useState('');
  const [extractLighting, setExtractLighting] = useState(true);
  const [extractComposition, setExtractComposition] = useState(true);
  const [extractAction, setExtractAction] = useState(true);

  return (
    <div className="container">
      <button onClick={() => navigate('/')} className="back-button">
        <ChevronLeft size={20} />
        Back to Dashboard
      </button>

      <div className="card">
        <h2>Video Frame Extractor</h2>

        <div className="form-group">
          <label className="form-label">Video File Path</label>
          <input
            type="text"
            placeholder="Enter path to video file..."
            value={videoPath}
            onChange={(e) => setVideoPath(e.target.value)}
            className="input"
          />
        </div>

        <div className="settings-box">
          <h3>Extraction Settings</h3>
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={extractLighting}
                onChange={(e) => setExtractLighting(e.target.checked)}
              />
              Extract frames with dramatic lighting
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={extractComposition}
                onChange={(e) => setExtractComposition(e.target.checked)}
              />
              Extract frames with strong composition
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={extractAction}
                onChange={(e) => setExtractAction(e.target.checked)}
              />
              Extract peak action/emotion moments
            </label>
          </div>
        </div>

        <button disabled={!videoPath} className="button button-red full-width">
          Analyze Video & Extract Frames
        </button>

        <div className="info-text">
          <p>Extracted frames will be saved to your reference collection</p>
          <p className="info-subtext">Note: This feature requires additional video processing setup</p>
        </div>
      </div>
    </div>
  );
}

// Progress Analytics Component
function ProgressAnalytics({ skills }) {
  const navigate = useNavigate();
  const [practiceStats, setPracticeStats] = useState(null);
  const [artworkStats, setArtworkStats] = useState(null);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [skillProgress, setSkillProgress] = useState(null);
  const [period, setPeriod] = useState('month');
  const [loading, setLoading] = useState(true);
  const [showSessionManager, setShowSessionManager] = useState(false);
  const [allSessions, setAllSessions] = useState([]);

  useEffect(() => {
    loadStats();
  }, [period]);

  useEffect(() => {
    if (selectedSkill) {
      loadSkillProgress(selectedSkill);
    }
  }, [selectedSkill]);

  const loadStats = async () => {
    setLoading(true);
    try {
      const [practiceRes, artworkRes] = await Promise.all([
        fetch(`${API_URL}/stats/practice?period=${period}`),
        fetch(`${API_URL}/stats/artwork`)
      ]);
      
      const practiceData = await practiceRes.json();
      const artworkData = await artworkRes.json();
      
      setPracticeStats(practiceData);
      setArtworkStats(artworkData);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
    setLoading(false);
  };

  const loadSkillProgress = async (skill) => {
    try {
      const response = await fetch(`${API_URL}/stats/skill-progress/${encodeURIComponent(skill)}`);
      const data = await response.json();
      setSkillProgress(data);
    } catch (error) {
      console.error('Failed to load skill progress:', error);
    }
  };

  const loadAllSessions = async () => {
    try {
      const response = await fetch(`${API_URL}/sessions`);
      const data = await response.json();
      setAllSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to load all sessions:', error);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!window.confirm('Are you sure you want to delete this session? This cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/sessions/${sessionId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await loadAllSessions();
        await loadStats();
      } else {
        console.error('Failed to delete session');
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  useEffect(() => {
    if (showSessionManager) {
      loadAllSessions();
    }
  }, [showSessionManager]);

  if (loading) {
    return (
      <div className="container">
        <button onClick={() => navigate('/')} className="back-button">
          <ChevronLeft size={20} />
          Back to Dashboard
        </button>
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container container-wide">
      <button onClick={() => navigate('/')} className="back-button">
        <ChevronLeft size={20} />
        Back to Dashboard
      </button>

      <div className="analytics-header">
        <h2>Progress & Analytics</h2>
        <p className="subtitle">Track your artistic development over time</p>
      </div>

      <div className="period-selector">
        {['week', 'month', 'year', 'all'].map(p => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`period-button ${period === p ? 'active' : ''}`}
          >
            {p === 'all' ? 'All Time' : `This ${p.charAt(0).toUpperCase() + p.slice(1)}`}
          </button>
        ))}
      </div>

      <div className="stats-cards">
        <div className="stat-card stat-card-blue">
          <div className="stat-content">
            <Clock size={32} />
            <span className="stat-value">{practiceStats?.totalHours || 0}h</span>
          </div>
          <p className="stat-label">Total Practice Time</p>
          <p className="stat-sublabel">{practiceStats?.totalSessions || 0} sessions</p>
        </div>

        <div className="stat-card stat-card-purple">
          <div className="stat-content">
            <Image size={32} />
            <span className="stat-value">{artworkStats?.totalArtwork || 0}</span>
          </div>
          <p className="stat-label">Artworks Created</p>
          <p className="stat-sublabel">{artworkStats?.recentArtworkCount || 0} this month</p>
        </div>

        <div className="stat-card stat-card-orange">
          <div className="stat-content">
            <Target size={32} />
            <span className="stat-value">{practiceStats?.totalImages || 0}</span>
          </div>
          <p className="stat-label">Reference Studies</p>
          <p className="stat-sublabel">Avg {practiceStats?.averageSessionMinutes || 0} min/session</p>
        </div>

        <div className="stat-card stat-card-green">
          <div className="stat-content">
            <Award size={32} />
            <span className="stat-value">{practiceStats?.currentStreak || 0}</span>
          </div>
          <p className="stat-label">Day Streak</p>
          <p className="stat-sublabel">Keep it up!</p>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="card">
          <h3 className="card-title">
            <BarChart3 size={20} />
            Practice by Skill
          </h3>
          <div className="skill-bars">
            {Object.entries(practiceStats?.practiceBySkill || {})
              .sort(([, a], [, b]) => b.minutes - a.minutes)
              .map(([skill, data]) => (
                <div key={skill} className="skill-bar-item">
                  <div className="skill-bar-header">
                    <button
                      onClick={() => setSelectedSkill(skill)}
                      className="skill-name-button"
                    >
                      {skill}
                    </button>
                    <span className="skill-hours">{Math.round(data.minutes / 60 * 10) / 10}h</span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-bar-fill progress-bar-teal"
                      style={{ 
                        width: `${(data.minutes / Math.max(...Object.values(practiceStats?.practiceBySkill || {}).map(d => d.minutes))) * 100}%` 
                      }}
                    />
                  </div>
                  <p className="skill-meta">{data.sessions} sessions • {data.images} images</p>
                </div>
              ))}
            {Object.keys(practiceStats?.practiceBySkill || {}).length === 0 && (
              <p className="empty-message">No practice data yet. Start a warmup session!</p>
            )}
          </div>
        </div>

        <div className="card">
          <h3 className="card-title">
            <Image size={20} />
            Artwork by Skill
          </h3>
          <div className="skill-bars">
            {Object.entries(artworkStats?.artworkBySkill || {})
              .sort(([, a], [, b]) => b - a)
              .map(([skill, count]) => (
                <div key={skill} className="skill-bar-item">
                  <div className="skill-bar-header">
                    <button
                      onClick={() => setSelectedSkill(skill)}
                      className="skill-name-button"
                    >
                      {skill}
                    </button>
                    <span className="skill-hours">{count} pieces</span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-bar-fill progress-bar-purple"
                      style={{ 
                        width: `${(count / Math.max(...Object.values(artworkStats?.artworkBySkill || {}))) * 100}%` 
                      }}
                    />
                  </div>
                </div>
              ))}
            {Object.keys(artworkStats?.artworkBySkill || {}).length === 0 && (
              <p className="empty-message">No artwork uploaded yet. Upload your first piece!</p>
            )}
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">
          <Calendar size={20} />
          Practice Activity
        </h3>
        <div className="activity-timeline">
          {Object.entries(practiceStats?.practiceByDay || {})
            .sort(([a], [b]) => b.localeCompare(a))
            .slice(0, 30)
            .map(([date, data]) => (
              <div key={date} className="activity-row">
                <span className="activity-date">{date}</span>
                <div className="activity-bar-container">
                  <div
                    className="activity-bar"
                    style={{ width: `${Math.min((data.minutes / 120) * 100, 100)}%` }}
                  >
                    {data.minutes > 10 && <span className="activity-text">{data.minutes}m</span>}
                  </div>
                </div>
                <span className="activity-sessions">{data.sessions} session{data.sessions !== 1 ? 's' : ''}</span>
              </div>
            ))}
          {Object.keys(practiceStats?.practiceByDay || {}).length === 0 && (
            <p className="empty-message">No practice activity recorded yet</p>
          )}
        </div>
      </div>

      {selectedSkill && skillProgress && (
        <div className="card skill-detail-card">
          <div className="skill-detail-header">
            <h3>{selectedSkill} Progress</h3>
            <button
              onClick={() => {
                setSelectedSkill(null);
                setSkillProgress(null);
              }}
              className="icon-button"
            >
              <X size={20} />
            </button>
          </div>

          <div className="skill-stats-grid">
            <div className="skill-stat-box">
              <p className="skill-stat-value skill-stat-blue">{skillProgress.totalPracticeSessions}</p>
              <p className="skill-stat-label">Practice Sessions</p>
              <p className="skill-stat-sublabel">{Math.round(skillProgress.totalPracticeMinutes / 60 * 10) / 10} hours</p>
            </div>
            <div className="skill-stat-box">
              <p className="skill-stat-value skill-stat-purple">{skillProgress.totalArtwork}</p>
              <p className="skill-stat-label">Artwork Created</p>
            </div>
            <div className="skill-stat-box">
              <p className="skill-stat-value skill-stat-green">{skillProgress.totalCritiques}</p>
              <p className="skill-stat-label">Critiques Received</p>
            </div>
          </div>

          <div className="skill-timeline">
            <h4>Activity Timeline</h4>
            <div className="timeline-items">
              {Object.entries(skillProgress.timeline || {})
                .sort(([a], [b]) => b.localeCompare(a))
                .map(([month, data]) => (
                  <div key={month} className="timeline-item">
                    <span className="timeline-month">{month}</span>
                    <div className="timeline-badges">
                      {data.practice > 0 && (
                        <span className="timeline-badge timeline-badge-blue">
                          {data.practice} practice
                        </span>
                      )}
                      {data.artwork > 0 && (
                        <span className="timeline-badge timeline-badge-purple">
                          {data.artwork} artwork
                        </span>
                      )}
                      {data.critiques > 0 && (
                        <span className="timeline-badge timeline-badge-green">
                          {data.critiques} critiques
                        </span>
                      )}
                    </div>
                  </div>
                ))}
            </div>
          </div>

          <div className="skill-recent-grid">
            <div>
              <h4>Recent Practice Sessions</h4>
              <div className="recent-items">
                {skillProgress.recentSessions?.slice(0, 5).map((session, idx) => (
                  <div key={idx} className="recent-item">
                    <p className="recent-title">{session.duration} minutes</p>
                    <p className="recent-date">{new Date(session.completedAt).toLocaleDateString()}</p>
                  </div>
                ))}
                {(!skillProgress.recentSessions || skillProgress.recentSessions.length === 0) && (
                  <p className="empty-message-small">No recent sessions</p>
                )}
              </div>
            </div>
            <div>
              <h4>Recent Artwork</h4>
              <div className="recent-items">
                {skillProgress.recentArtwork?.slice(0, 5).map((art, idx) => (
                  <div key={idx} className="recent-item">
                    <p className="recent-title">{art.originalName || 'Untitled'}</p>
                    <p className="recent-date">{new Date(art.uploadedAt).toLocaleDateString()}</p>
                  </div>
                ))}
                {(!skillProgress.recentArtwork || skillProgress.recentArtwork.length === 0) && (
                  <p className="empty-message-small">No artwork yet</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="card insights-card">
        <h3 className="card-title">
          <TrendingUp size={20} />
          Insights & Recommendations
        </h3>
        <div className="insights-grid">
          {practiceStats?.currentStreak > 0 && (
            <div className="insight-box insight-green">
              <p className="insight-title">🔥 Great Consistency!</p>
              <p className="insight-text">You've practiced {practiceStats.currentStreak} days in a row. Keep it up!</p>
            </div>
          )}
          {practiceStats?.currentStreak === 0 && (
            <div className="insight-box insight-green">
              <p className="insight-title">💡 Start a Streak</p>
              <p className="insight-text">Practice today to start building consistency!</p>
            </div>
          )}
          {Object.keys(practiceStats?.practiceBySkill || {}).length > 0 && (
            <div className="insight-box insight-teal">
              <p className="insight-title">🎯 Most Practiced</p>
              <p className="insight-text">
                Your top skill is {Object.entries(practiceStats.practiceBySkill).sort(([,a], [,b]) => b.minutes - a.minutes)[0][0]}
              </p>
            </div>
          )}
          {artworkStats?.totalArtwork >= 10 && (
            <div className="insight-box insight-teal">
              <p className="insight-title">🎨 Prolific Artist!</p>
              <p className="insight-text">You've created {artworkStats.totalArtwork} pieces of artwork!</p>
            </div>
          )}
          {practiceStats?.totalHours >= 10 && (
            <div className="insight-box insight-teal">
              <p className="insight-title">⏰ Dedicated Practice</p>
              <p className="insight-text">{practiceStats.totalHours} hours of focused practice time!</p>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="session-manager-header">
          <h3 className="card-title">
            <Calendar size={20} />
            Session Management
          </h3>
          <button
            onClick={() => setShowSessionManager(!showSessionManager)}
            className="session-manager-toggle"
          >
            {showSessionManager ? 'Hide Sessions' : 'Manage Sessions'}
          </button>
        </div>

        {showSessionManager && (
          <div className="session-list">
            {allSessions.length === 0 ? (
              <p className="empty-message">No sessions recorded yet</p>
            ) : (
              <div className="sessions-table">
                <div className="sessions-table-header">
                  <span>Date</span>
                  <span>Type</span>
                  <span>Duration</span>
                  <span>Images</span>
                  <span>Skills</span>
                  <span>Actions</span>
                </div>
                {allSessions
                  .sort((a, b) => new Date(b.completedAt) - new Date(a.completedAt))
                  .map(session => (
                    <div key={session.id} className="sessions-table-row">
                      <span className="session-date">
                        {new Date(session.completedAt).toLocaleDateString()}
                        <br />
                        <small>{new Date(session.completedAt).toLocaleTimeString()}</small>
                      </span>
                      <span className="session-type">
                        <span className={`session-type-badge session-type-${session.type}`}>
                          {session.type}
                        </span>
                      </span>
                      <span className="session-duration">{session.duration} min</span>
                      <span className="session-images">{session.imageCount} images</span>
                      <span className="session-skills">
                        {session.skills && session.skills.length > 0
                          ? session.skills.join(', ')
                          : 'None'}
                      </span>
                      <span className="session-actions">
                        <button
                          onClick={() => deleteSession(session.id)}
                          className="delete-session-button"
                          title="Delete this session"
                        >
                          <X size={16} />
                        </button>
                      </span>
                    </div>
                  ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function AdminPanel() {
  const [searchParams] = useSearchParams();
  const [authStatus, setAuthStatus] = useState(null);
  const [syncedAlbums, setSyncedAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState({});
  const [indexerStatus, setIndexerStatus] = useState(null);
  const [indexerLoading, setIndexerLoading] = useState(false);
  const [startingIndexer, setStartingIndexer] = useState(false);

  useEffect(() => {
    checkAuthStatus();
    loadSyncedAlbums();
    loadIndexerStatus();

    // Poll indexer status every 2 seconds (always, to show progress and updates)
    const statusPoll = setInterval(loadIndexerStatus, 2000);
    return () => clearInterval(statusPoll);
  }, [searchParams]);

  const loadIndexerStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/indexer-status`);
      const data = await response.json();
      setIndexerStatus(data);
    } catch (error) {
      console.error('Failed to load indexer status:', error);
    }
  };

  const startIndexer = async () => {
    try {
      setStartingIndexer(true);
      const response = await fetch(`${API_URL}/indexer/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        const errorData = await response.json();
        alert(`Failed to start indexer: ${errorData.detail || response.statusText}`);
        return;
      }

      const data = await response.json();
      if (data.success) {
        alert('Photo indexer started! Indexing will run in the background. Check status below for progress.');
        // Load status immediately
        await loadIndexerStatus();
      } else {
        alert(`Failed to start indexer: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Failed to start indexer:', error);
      alert('Failed to start indexer. Check console for details.');
    } finally {
      setStartingIndexer(false);
    }
  };

  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/google-photos/auth-status`);
      const data = await response.json();
      setAuthStatus(data);
    } catch (error) {
      console.error('Failed to check auth status:', error);
    } finally {
      setLoading(false);
    }
  };

  const openGooglePhotosPicker = async () => {
    try {
      // Create a picker session
      const response = await fetch(`${API_URL}/google-photos/picker/create-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (!response.ok) {
        alert(`Failed to create picker session: ${data.detail}`);
        return;
      }

      const { session_id, picker_uri, polling_config } = data;

      // Open the picker in a new window
      const pickerWindow = window.open(picker_uri, 'GooglePhotosPicker', 'width=800,height=600');

      // Poll for completion
      const pollInterval = polling_config?.pollInterval || 5000; // Default to 5 seconds
      const pollSession = async () => {
        try {
          const statusResponse = await fetch(`${API_URL}/google-photos/picker/session/${session_id}`);
          const statusData = await statusResponse.json();

          if (statusData.media_items_set) {
            // User has finished selecting photos
            if (pickerWindow && !pickerWindow.closed) {
              pickerWindow.close();
            }

            // Fetch the selected media items
            const mediaResponse = await fetch(`${API_URL}/google-photos/picker/session/${session_id}/media-items`);
            const mediaData = await mediaResponse.json();

            if (mediaData.count > 0) {
              alert(`You selected ${mediaData.count} photos. Downloading now...`);
              await downloadPickerPhotos(mediaData.media_items);
            } else {
              alert('No photos were selected.');
            }
          } else if (!pickerWindow || pickerWindow.closed) {
            // User closed the window without selecting
            console.log('Picker window closed by user');
          } else {
            // Continue polling
            setTimeout(pollSession, pollInterval);
          }
        } catch (error) {
          console.error('Error polling picker session:', error);
        }
      };

      // Start polling
      setTimeout(pollSession, pollInterval);

    } catch (error) {
      console.error('Failed to open Google Photos Picker:', error);
      alert('Failed to open Google Photos Picker');
    }
  };

  const downloadPickerPhotos = async (mediaItems) => {
    try {
      const response = await fetch(`${API_URL}/google-photos/download-selected-photos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          media_items: mediaItems.map(item => ({
            id: item.id,
            baseUrl: item.mediaFile?.url || item.baseUrl,
            filename: item.filename
          }))
        })
      });

      const result = await response.json();

      if (response.ok && result.status === 'success') {
        alert(`Successfully downloaded ${result.downloaded_count} photos from Google Photos!`);
        await loadSyncedAlbums();
      } else {
        alert(`Download completed with some errors: ${result.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Failed to download photos:', error);
      alert('Failed to download photos');
    }
  };

  const loadSyncedAlbums = async () => {
    try {
      const response = await fetch(`${API_URL}/google-photos/synced-albums`);
      const data = await response.json();
      setSyncedAlbums(data.synced_albums || []);
    } catch (error) {
      console.error('Failed to load synced albums:', error);
    }
  };

  const startOAuth = async () => {
    try {
      const response = await fetch(`${API_URL}/google-photos/auth-url`);
      const data = await response.json();

      if (data.auth_url) {
        window.location.href = data.auth_url;
      }
    } catch (error) {
      console.error('Failed to start OAuth:', error);
    }
  };

  const syncAlbum = async (albumId, albumTitle) => {
    setSyncing(prev => ({ ...prev, [albumId]: true }));
    try {
      const response = await fetch(`${API_URL}/google-photos/sync-album`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ album_id: albumId })
      });

      const data = await response.json();

      if (data.success) {
        alert(`Successfully synced ${data.photos_downloaded} photos from "${albumTitle}"`);
        await loadSyncedAlbums();
      } else {
        alert(`Failed to sync album: ${data.error}`);
      }
    } catch (error) {
      console.error('Failed to sync album:', error);
      alert('Failed to sync album');
    } finally {
      setSyncing(prev => ({ ...prev, [albumId]: false }));
    }
  };


  if (loading) {
    return (
      <div className="admin-panel">
        <div className="admin-header">
          <h2>Admin Panel</h2>
          <button onClick={() => window.history.back()} className="back-button">
            <ChevronLeft size={20} />
            Back to Dashboard
          </button>
        </div>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h2>Admin Panel</h2>
        <button onClick={() => window.history.back()} className="back-button">
          <ChevronLeft size={20} />
          Back to Dashboard
        </button>
      </div>

      {/* Photo Indexer Status */}
      <div className="admin-section">
        <h3>Photo Indexer Status</h3>

        {indexerStatus && (
          <div className={`indexer-status-box ${indexerStatus.isRunning ? 'status-running' : 'status-idle'}`}>
            {indexerStatus.isRunning ? (
              <>
                <div className="status-indicator running"></div>
                <div className="status-info">
                  <div className="status-title">Indexing in Progress</div>
                  <div className="status-collection">{indexerStatus.collection}</div>
                  <div className="status-progress">
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${indexerStatus.percentage}%` }}></div>
                    </div>
                    <div className="progress-text">
                      {indexerStatus.current} / {indexerStatus.total} images ({indexerStatus.percentage}%)
                    </div>
                  </div>
                  {indexerStatus.currentImage && (
                    <div className="current-image">Current: {indexerStatus.currentImage}</div>
                  )}
                  {indexerStatus.updatedAt && (
                    <div className="updated-at">Last updated: {new Date(indexerStatus.updatedAt).toLocaleTimeString()}</div>
                  )}
                  {indexerStatus.estimatedTimeRemainingFormatted && (
                    <div className="estimated-time">Estimated time remaining: {indexerStatus.estimatedTimeRemainingFormatted}</div>
                  )}
                </div>
              </>
            ) : (
              <>
                <div className="status-indicator idle"></div>
                <div className="status-info">
                  <div className="status-title">Indexer Idle</div>
                  <div className="status-message">{indexerStatus.message || 'No indexing process running'}</div>
                  {indexerStatus.completedAt && (
                    <div className="last-indexed">Last Indexed: {new Date(indexerStatus.completedAt).toLocaleString()}</div>
                  )}
                  {indexerStatus.averageDurationFormatted && (
                    <div className="execution-stats">
                      <div className="stat-row">
                        <span className="stat-label">Average time:</span>
                        <span className="stat-value">{indexerStatus.averageDurationFormatted}</span>
                      </div>
                      {indexerStatus.executionHistory && indexerStatus.executionHistory.length > 0 && (
                        <div className="execution-history">
                          <div className="stat-label">Last {indexerStatus.executionHistory.length} runs:</div>
                          {indexerStatus.executionHistory.map((run, idx) => (
                            <div key={idx} className="history-item">
                              {run.durationFormatted} - {new Date(run.completedAt).toLocaleDateString()}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                  <button
                    onClick={startIndexer}
                    disabled={startingIndexer}
                    className="button button-primary"
                    style={{ marginTop: '12px' }}
                  >
                    {startingIndexer ? (
                      <>
                        <div className="loading-spinner-small"></div>
                        Starting...
                      </>
                    ) : (
                      <>Start Photo Indexing</>
                    )}
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Google Photos Connection Status */}
      <div className="admin-section">
        <h3>Google Photos Integration</h3>

        {authStatus && (
          <div className={`status-box ${authStatus.authenticated ? 'status-success' : 'status-warning'}`}>
            {authStatus.authenticated ? (
              <>
                <Check size={20} />
                <span>Connected to Google Photos</span>
              </>
            ) : (
              <>
                <AlertCircle size={20} />
                <span>{authStatus.message}</span>
              </>
            )}
          </div>
        )}

        {!authStatus?.authenticated && (
          <button onClick={startOAuth} className="connect-button">
            <Settings size={18} />
            Connect Google Photos
          </button>
        )}

        {authStatus?.authenticated && (
          <button onClick={openGooglePhotosPicker} className="connect-button" style={{ marginTop: '12px' }}>
            <Camera size={18} />
            Select Photos from Google Photos
          </button>
        )}
      </div>

      {/* Synced Albums */}
      {syncedAlbums.length > 0 && (
        <div className="admin-section">
          <h3>Synced Albums</h3>
          <div className="synced-albums-list">
            {syncedAlbums.map(album => (
              <div key={album.album_id} className="synced-album-item">
                <div className="synced-album-info">
                  <h4>{album.title}</h4>
                  <p>{album.photo_count} photos • Last synced: {new Date(album.last_synced).toLocaleDateString()}</p>
                </div>
                <button
                  onClick={() => syncAlbum(album.album_id, album.title)}
                  disabled={syncing[album.album_id]}
                  className="resync-button"
                >
                  {syncing[album.album_id] ? (
                    <>
                      <div className="loading-spinner-small"></div>
                      Syncing...
                    </>
                  ) : (
                    <>
                      <RefreshCw size={16} />
                      Re-sync
                    </>
                  )}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}

function PaintManager() {
  const [paints, setPaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingPaint, setEditingPaint] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    pigment: '',
    rgb: null
  });
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadPaints();
  }, []);

  const loadPaints = async () => {
    try {
      const response = await fetch(`${API_URL}/paints`);
      const data = await response.json();
      setPaints(data.paints || []);
    } catch (error) {
      console.error('Failed to load paints:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const url = editingPaint
        ? `${API_URL}/paints/${editingPaint.id}`
        : `${API_URL}/paints`;

      const method = editingPaint ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.success) {
        await loadPaints();
        resetForm();
      }
    } catch (error) {
      console.error('Failed to save paint:', error);
    }
  };

  const handleDelete = async (paintId) => {
    if (!window.confirm('Are you sure you want to delete this paint?')) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/paints/${paintId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await loadPaints();
      }
    } catch (error) {
      console.error('Failed to delete paint:', error);
    }
  };

  const handleEdit = (paint) => {
    setEditingPaint(paint);
    setFormData({
      name: paint.name || '',
      pigment: paint.pigment || '',
      rgb: paint.rgb || null
    });
    setShowAddForm(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      pigment: '',
      rgb: null
    });
    setEditingPaint(null);
    setShowAddForm(false);
  };

  const lookupColor = async () => {
    // Try pigment code first, fall back to name
    const colorToLookup = formData.pigment || formData.name;
    if (!colorToLookup) return;

    try {
      const response = await fetch(`${API_URL}/paints/lookup-color`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ color: colorToLookup })
      });

      const data = await response.json();

      if (data.success) {
        setFormData({ ...formData, rgb: data.rgb });
      } else {
        alert('Could not find RGB values for this color name or pigment code. You can enter them manually.');
      }
    } catch (error) {
      console.error('Failed to lookup color:', error);
    }
  };

  const filteredPaints = paints.filter(paint =>
    paint.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    paint.pigment?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="paint-manager">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading paints...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="paint-manager">
      <div className="paint-header">
        <div>
          <h2>Paint Manager</h2>
          <p className="paint-subtitle">Track your paints and pigments with RGB values</p>
        </div>
        <button onClick={() => window.history.back()} className="back-button">
          <ChevronLeft size={20} />
          Back to Dashboard
        </button>
      </div>

      {/* Search and Add */}
      <div className="paint-controls">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search paints by name or pigment..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input-paint"
          />
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="add-paint-button"
        >
          {showAddForm ? <X size={18} /> : <Plus size={18} />}
          {showAddForm ? 'Cancel' : 'Add Paint'}
        </button>
      </div>

      {/* Add/Edit Form */}
      {showAddForm && (
        <div className="paint-form-container">
          <h3>{editingPaint ? 'Edit Paint' : 'Add New Paint'}</h3>
          <form onSubmit={handleSubmit} className="paint-form">
            <div className="form-group">
              <label>Paint Name *</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Cadmium Red"
              />
            </div>

            <div className="form-group">
              <label>Pigment Code</label>
              <input
                type="text"
                value={formData.pigment}
                onChange={(e) => setFormData({ ...formData, pigment: e.target.value })}
                placeholder="e.g., PR108"
              />
            </div>

            <div className="form-group">
              <label>RGB Values</label>
              <div className="rgb-controls">
                <button
                  type="button"
                  onClick={lookupColor}
                  className="lookup-button"
                >
                  <Search size={16} />
                  Lookup Color
                </button>
                {formData.rgb && (
                  <div className="rgb-preview">
                    <div
                      className="color-swatch"
                      style={{
                        backgroundColor: `rgb(${formData.rgb.r}, ${formData.rgb.g}, ${formData.rgb.b})`
                      }}
                    />
                    <span>RGB({formData.rgb.r}, {formData.rgb.g}, {formData.rgb.b})</span>
                  </div>
                )}
              </div>
              <div className="rgb-inputs">
                <input
                  type="number"
                  min="0"
                  max="255"
                  placeholder="R"
                  value={formData.rgb?.r || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    rgb: { ...formData.rgb, r: parseInt(e.target.value) || 0 }
                  })}
                />
                <input
                  type="number"
                  min="0"
                  max="255"
                  placeholder="G"
                  value={formData.rgb?.g || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    rgb: { ...formData.rgb, g: parseInt(e.target.value) || 0 }
                  })}
                />
                <input
                  type="number"
                  min="0"
                  max="255"
                  placeholder="B"
                  value={formData.rgb?.b || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    rgb: { ...formData.rgb, b: parseInt(e.target.value) || 0 }
                  })}
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="submit-button">
                {editingPaint ? 'Update Paint' : 'Add Paint'}
              </button>
              <button type="button" onClick={resetForm} className="cancel-button">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Paints List */}
      <div className="paints-list">
        <h3>Your Paints ({filteredPaints.length})</h3>
        {filteredPaints.length === 0 ? (
          <div className="empty-state">
            <Palette size={48} />
            <p>No paints found</p>
            <p className="empty-hint">Add your first paint to get started!</p>
          </div>
        ) : (
          <div className="paints-grid">
            {filteredPaints.map(paint => (
              <div key={paint.id} className="paint-card">
                <div className="paint-card-header">
                  {paint.rgb && (
                    <div
                      className="paint-color-swatch"
                      style={{
                        backgroundColor: `rgb(${paint.rgb.r}, ${paint.rgb.g}, ${paint.rgb.b})`
                      }}
                    />
                  )}
                  <div className="paint-card-info">
                    <h4>{paint.name}</h4>
                  </div>
                </div>
                <div className="paint-card-details">
                  {paint.pigment && (
                    <div className="paint-detail">
                      <span className="detail-label">Pigment:</span>
                      <span>{paint.pigment}</span>
                    </div>
                  )}
                  {paint.rgb && (
                    <div className="paint-detail">
                      <span className="detail-label">RGB:</span>
                      <span className="rgb-value">
                        {paint.rgb.r}, {paint.rgb.g}, {paint.rgb.b}
                      </span>
                    </div>
                  )}
                </div>
                <div className="paint-card-actions">
                  <button
                    onClick={() => handleEdit(paint)}
                    className="edit-paint-button"
                    title="Edit paint"
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    onClick={() => handleDelete(paint.id)}
                    className="delete-paint-button"
                    title="Delete paint"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}