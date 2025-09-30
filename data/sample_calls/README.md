# 📞 Sample Calls Directory
**Designer: Abdullah Alawiss**

This directory contains comprehensive test data for the AI Callcenter Agent, specifically designed for Norwegian telecom compliance analysis.

## 📁 **Available Files:**

### 📝 **Text Transcriptions:**
- **`norwegian_telecom_call_sample.txt`** - Original sample with multiple issues
- **`good_call_compliant.txt`** - Perfect compliance example (Score: 10/10)
- **`bad_call_violations.txt`** - Multiple serious violations (Score: 1/10)
- **`bindingstid_problem.txt`** - Binding period avoidance issues (Score: 3/10)

### 📊 **Data Files:**
- **`call_logs.csv`** - Comprehensive call history with 25 sample records
- **`test_scenarios.json`** - Configuration for Norwegian compliance testing
- **`audio_samples_info.txt`** - Mock audio file specifications

## 🇳🇴 **Norwegian Compliance Focus:**

### **Key Violation Types Tested:**
- **Bindingstid Missing** - Failure to disclose binding periods
- **Price Incomplete** - Insufficient pricing transparency  
- **Excessive Pressure** - High-pressure sales tactics
- **GDPR Violations** - Improper data collection
- **False Marketing** - Misleading claims and promises

### **Compliance Indicators:**
- ✅ **Positive Signals**: Clear bindingstid, transparent pricing, angrerett mention
- ❌ **Negative Signals**: Pressure tactics, vague terms, misleading claims

## 🎯 **Test Scenarios:**

### **1. Perfect Compliance (`good_call_compliant.txt`)**
- Demonstrates ideal Norwegian telecom sales approach
- All legal requirements met
- Professional customer interaction
- Score: 10/10

### **2. Multiple Violations (`bad_call_violations.txt`)**
- Shows serious compliance breaches
- Educational "what not to do" example
- Multiple Norwegian law violations
- Score: 1/10

### **3. Binding Period Issues (`bindingstid_problem.txt`)**
- Focuses on bindingstid disclosure problems
- Common real-world scenario
- Agent avoidance patterns
- Score: 3/10

## 📈 **CSV Data Structure:**
The `call_logs.csv` contains:
- **25 sample call records**
- **Realistic Norwegian operator names** (Telenor, Telia, Ice, OneCall)
- **Compliance scoring** (1-10 scale)
- **Violation categorization**
- **GDPR compliance tracking**
- **Sales pressure level assessment**

## 🔧 **JSON Configuration:**
The `test_scenarios.json` provides:
- **Norwegian market data** (operator market share)
- **Product type specifications**
- **Violation type definitions** with Norwegian law references
- **Compliance weight settings**
- **Quality threshold definitions**

## 🎵 **Audio File Information:**
While actual audio files are not included, `audio_samples_info.txt` describes:
- **8 mock audio samples** representing different scenarios
- **Technical specifications** (quality, duration, file size)
- **Speaker information** (agent/customer gender combinations)
- **Processing pipeline** details

## 📋 **Usage Instructions:**

### **For Testing:**
1. Upload any `.txt` file to test transcription analysis
2. Use CSV for bulk data analysis simulation
3. Reference JSON for compliance rule configuration

### **For Development:**
1. Text files serve as transcription examples
2. CSV provides database seeding data
3. JSON offers configuration templates

### **For Demo:**
1. Show perfect vs. problematic calls
2. Demonstrate Norwegian compliance detection
3. Exhibit GDPR-compliant data handling

## 🚀 **Quick Start:**
```bash
# Test with a compliant call
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -F "file=@data/sample_calls/good_call_compliant.txt"

# Test with violations
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -F "file=@data/sample_calls/bad_call_violations.txt"

# Get analysis results
curl http://localhost:8000/api/v1/analysis/violations
```

## 🔍 **Analysis Features:**
- **Real-time compliance scoring**
- **Norwegian law reference mapping**
- **GDPR redaction simulation**
- **Sales pressure detection**
- **Bindingstid disclosure validation**
- **Price transparency assessment**

---

**🇳🇴 Tilpasset norske telekomregler og GDPR-krav**
**🔒 GDPR-compliant data processing**
**📊 Comprehensive compliance reporting**

*All sample data is fictional and created for testing purposes only.*
