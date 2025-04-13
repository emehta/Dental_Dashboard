// Dental Clinic Dataset Generator for CFO Analytics
// This script creates a realistic dataset of dental appointments, procedures, and financial data
// Can be run in Node.js with lodash and papaparse packages installed

const fs = require('fs');

// Helper function to generate random numbers within a range
function randomBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

// Helper function to generate random dates within a range
function randomDate(start, end) {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
}

// Helper function to format dates as YYYY-MM-DD
function formatDate(date) {
  return date.toISOString().split('T')[0];
}

// Constants for the dataset
const START_DATE = new Date(2020, 0, 1); // Jan 1, 2020
const END_DATE = new Date(2025, 3, 1);   // Apr 1, 2025
const NUM_RECORDS = 250;                 // Number of appointment records
const NUM_PATIENTS = 75;                 // Number of unique patients

// Create location data
const locations = [
  { id: 'LOC001', name: 'Downtown Dental', address: '123 Main St, Portland, OR 97201', google_rating: 4.8, opened_date: '2015-03-15', services_offered: 'General|Cosmetic|Orthodontic|Pediatric|Implants' },
  { id: 'LOC002', name: 'Westside Smile Center', address: '456 Park Ave, Portland, OR 97229', google_rating: 4.6, opened_date: '2017-06-22', services_offered: 'General|Cosmetic|Periodontic|Implants|Emergency' },
  { id: 'LOC003', name: 'East Valley Dental Care', address: '789 River Rd, Gresham, OR 97030', google_rating: 4.5, opened_date: '2019-11-10', services_offered: 'General|Cosmetic|Pediatric|Emergency' }
];

// Create provider data
const providers = [
  { id: 'DR001', name: 'Dr. Sarah Johnson', role: 'Dentist', primary_location: 'LOC001', specialty: 'General' },
  { id: 'DR002', name: 'Dr. Michael Chen', role: 'Dentist', primary_location: 'LOC001', specialty: 'Orthodontics' },
  { id: 'DR003', name: 'Dr. Robert Garcia', role: 'Dentist', primary_location: 'LOC002', specialty: 'Periodontics' },
  { id: 'DR004', name: 'Dr. Emily Wilson', role: 'Dentist', primary_location: 'LOC002', specialty: 'General' },
  { id: 'DR005', name: 'Dr. David Kim', role: 'Dentist', primary_location: 'LOC003', specialty: 'General' },
  { id: 'HYG001', name: 'Lisa Martinez', role: 'Hygienist', primary_location: 'LOC001', specialty: 'Hygiene' },
  { id: 'HYG002', name: 'John Anderson', role: 'Hygienist', primary_location: 'LOC002', specialty: 'Hygiene' },
  { id: 'HYG003', name: 'Sophia Lee', role: 'Hygienist', primary_location: 'LOC003', specialty: 'Hygiene' }
];

// Create insurance provider data
const insuranceProviders = [
  { name: 'Delta Dental', avg_reimbursement_rate: 0.85 },
  { name: 'Cigna Dental', avg_reimbursement_rate: 0.80 },
  { name: 'Aetna', avg_reimbursement_rate: 0.75 },
  { name: 'MetLife', avg_reimbursement_rate: 0.82 },
  { name: 'Guardian', avg_reimbursement_rate: 0.78 },
  { name: 'No Insurance', avg_reimbursement_rate: 1.00 } // Self-pay
];

// Create procedure categories and codes
const procedures = [
  // Diagnostic
  { code: 'D0120', description: 'Periodic Oral Evaluation', category: 'Diagnostic', avg_fee: 60, duration: 15 },
  { code: 'D0150', description: 'Comprehensive Oral Evaluation', category: 'Diagnostic', avg_fee: 110, duration: 30 },
  { code: 'D0210', description: 'Complete Series X-rays', category: 'Diagnostic', avg_fee: 150, duration: 30 },
  { code: 'D0220', description: 'Periapical X-ray (First Film)', category: 'Diagnostic', avg_fee: 35, duration: 10 },
  { code: 'D0274', description: 'Bitewing X-rays (Four Films)', category: 'Diagnostic', avg_fee: 70, duration: 15 },
  
  // Preventive
  { code: 'D1110', description: 'Prophylaxis (Cleaning) - Adult', category: 'Preventive', avg_fee: 110, duration: 45 },
  { code: 'D1120', description: 'Prophylaxis (Cleaning) - Child', category: 'Preventive', avg_fee: 85, duration: 30 },
  { code: 'D1208', description: 'Fluoride Treatment', category: 'Preventive', avg_fee: 45, duration: 15 },
  { code: 'D1351', description: 'Sealant (Per Tooth)', category: 'Preventive', avg_fee: 60, duration: 20 },
  
  // Restorative
  { code: 'D2140', description: 'Amalgam Filling - One Surface', category: 'Restorative', avg_fee: 155, duration: 45 },
  { code: 'D2150', description: 'Amalgam Filling - Two Surfaces', category: 'Restorative', avg_fee: 195, duration: 60 },
  { code: 'D2160', description: 'Amalgam Filling - Three Surfaces', category: 'Restorative', avg_fee: 235, duration: 75 },
  { code: 'D2330', description: 'Resin Filling - One Surface', category: 'Restorative', avg_fee: 175, duration: 45 },
  { code: 'D2331', description: 'Resin Filling - Two Surfaces', category: 'Restorative', avg_fee: 215, duration: 60 },
  { code: 'D2332', description: 'Resin Filling - Three Surfaces', category: 'Restorative', avg_fee: 255, duration: 75 },
  { code: 'D2740', description: 'Crown - Porcelain/Ceramic', category: 'Restorative', avg_fee: 1250, duration: 90 },
  { code: 'D2750', description: 'Crown - Porcelain Fused to Metal', category: 'Restorative', avg_fee: 1150, duration: 90 },
  
  // Endodontics
  { code: 'D3310', description: 'Root Canal - Anterior', category: 'Endodontic', avg_fee: 825, duration: 90 },
  { code: 'D3320', description: 'Root Canal - Bicuspid', category: 'Endodontic', avg_fee: 950, duration: 105 },
  { code: 'D3330', description: 'Root Canal - Molar', category: 'Endodontic', avg_fee: 1150, duration: 120 },
  
  // Periodontics
  { code: 'D4341', description: 'Periodontal Scaling & Root Planing (Per Quadrant)', category: 'Periodontic', avg_fee: 275, duration: 60 },
  { code: 'D4910', description: 'Periodontal Maintenance', category: 'Periodontic', avg_fee: 135, duration: 45 },
  
  // Prosthodontics
  { code: 'D5110', description: 'Complete Denture - Maxillary', category: 'Prosthodontic', avg_fee: 1850, duration: 90 },
  { code: 'D5120', description: 'Complete Denture - Mandibular', category: 'Prosthodontic', avg_fee: 1850, duration: 90 },
  { code: 'D5213', description: 'Partial Denture - Maxillary', category: 'Prosthodontic', avg_fee: 1650, duration: 90 },
  { code: 'D5214', description: 'Partial Denture - Mandibular', category: 'Prosthodontic', avg_fee: 1650, duration: 90 },
  
  // Implants
  { code: 'D6010', description: 'Surgical Implant Placement', category: 'Implant', avg_fee: 2100, duration: 120 },
  { code: 'D6056', description: 'Implant Abutment', category: 'Implant', avg_fee: 650, duration: 60 },
  { code: 'D6058', description: 'Implant Crown', category: 'Implant', avg_fee: 1550, duration: 90 },
  
  // Orthodontics
  { code: 'D8080', description: 'Comprehensive Orthodontic Treatment - Adolescent', category: 'Orthodontic', avg_fee: 5500, duration: 120 },
  { code: 'D8090', description: 'Comprehensive Orthodontic Treatment - Adult', category: 'Orthodontic', avg_fee: 6200, duration: 120 },
  
  // Adjunctive Services
  { code: 'D9110', description: 'Palliative Treatment (Emergency)', category: 'Adjunctive', avg_fee: 125, duration: 30 },
  { code: 'D9215', description: 'Local Anesthesia', category: 'Adjunctive', avg_fee: 45, duration: 10 },
  { code: 'D9310', description: 'Consultation', category: 'Adjunctive', avg_fee: 95, duration: 45 }
];

// Define common teeth for dental procedures
const teeth = [
  '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16',  // Upper teeth (1-16)
  '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32'  // Lower teeth (17-32)
];

// Generate patient data
function generatePatients() {
  const patients = [];
  const genders = ['Male', 'Female'];
  const firstNamesMale = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles'];
  const firstNamesFemale = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen'];
  const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis', 'Garcia', 'Rodriguez', 'Wilson'];
  const zipCodes = ['97201', '97202', '97203', '97204', '97205'];
  
  for (let i = 1; i <= NUM_PATIENTS; i++) {
    const gender = genders[Math.floor(Math.random() * genders.length)];
    const firstName = gender === 'Male' 
      ? firstNamesMale[Math.floor(Math.random() * firstNamesMale.length)] 
      : firstNamesFemale[Math.floor(Math.random() * firstNamesFemale.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    
    // Age between 18 and 85
    const age = randomBetween(18, 85);
    
    // 80% have insurance
    const hasInsurance = Math.random() < 0.8;
    const insuranceProvider = hasInsurance 
      ? insuranceProviders[Math.floor(Math.random() * (insuranceProviders.length - 1))].name
      : 'No Insurance';
    
    // Registration date between 2018 and 2024
    const regYear = randomBetween(2018, 2024);
    const regMonth = randomBetween(1, 12);
    const regDay = randomBetween(1, 28);
    const registrationDate = `${regYear}-${String(regMonth).padStart(2, '0')}-${String(regDay).padStart(2, '0')}`;
    
    patients.push({
      patient_id: `PAT${String(i).padStart(4, '0')}`,
      first_name: firstName,
      last_name: lastName,
      name: `${firstName} ${lastName}`,
      gender: gender,
      age: age,
      zip_code: zipCodes[Math.floor(Math.random() * zipCodes.length)],
      registration_date: registrationDate,
      insurance_provider: insuranceProvider,
      is_active: Math.random() < 0.9 // 90% of patients are active
    });
  }
  
  return patients;
}

// Generate appointments and procedures
function generateAppointmentData(patients) {
  const appointments = [];
  const appointmentStatuses = ['Completed', 'No-Show', 'Canceled', 'Rescheduled'];
  const statusProbabilities = [0.85, 0.05, 0.07, 0.03]; // 85% completed, 5% no-show, etc.
  const paymentMethods = ['Credit Card', 'Debit Card', 'Cash', 'Check', 'Insurance Only'];
  
  for (let i = 0; i < NUM_RECORDS; i++) {
    // Select a random patient with bias toward frequent visitors
    const patientIndex = Math.floor(Math.pow(Math.random(), 1.5) * patients.length);
    const patient = patients[patientIndex];
    
    // Create visit date (between registration date and END_DATE)
    const regDate = new Date(patient.registration_date);
    const visitDate = randomDate(regDate > START_DATE ? regDate : START_DATE, END_DATE);
    const formattedVisitDate = formatDate(visitDate);
    
    // Extract year and month
    const year = visitDate.getFullYear();
    const month = visitDate.getMonth() + 1;
    
    // Select location and provider
    const location = locations[Math.floor(Math.random() * locations.length)];
    const provider = providers[Math.floor(Math.random() * providers.length)];
    
    // Determine appointment status
    let statusRand = Math.random();
    let statusIndex = 0;
    let cumulativeProb = 0;
    
    for (let j = 0; j < statusProbabilities.length; j++) {
      cumulativeProb += statusProbabilities[j];
      if (statusRand <= cumulativeProb) {
        statusIndex = j;
        break;
      }
    }
    
    const appointmentStatus = appointmentStatuses[statusIndex];
    
    // Visit ID
    const visitId = `V${String(i + 1).padStart(6, '0')}`;
    
    // Select 1-3 procedures for this visit
    const numProceduresForVisit = randomBetween(1, 3);
    
    for (let p = 0; p < numProceduresForVisit; p++) {
      // Select a procedure (weighted toward common procedures)
      let procedureIndex;
      if (Math.random() < 0.6) { // 60% chance of common procedure
        procedureIndex = Math.floor(Math.random() * 10); // First 10 are common procedures
      } else {
        procedureIndex = Math.floor(Math.random() * procedures.length);
      }
      
      const procedure = procedures[procedureIndex];
      
      // Procedure ID
      const procedureId = `PROC${String(i * 10 + p + 1).padStart(6, '0')}`;
      
      // Only proceed with financial calculations if the appointment was completed
      if (appointmentStatus === 'Completed') {
        // Financial calculations
        const chargedAmount = Math.round(procedure.avg_fee * (0.9 + Math.random() * 0.2));
        
        // Insurance calculations
        const hasInsurance = patient.insurance_provider !== 'No Insurance';
        let insuranceCovered = 0;
        
        if (hasInsurance) {
          // Different insurance providers cover different percentages
          let coverageRate = 0;
          const provider = insuranceProviders.find(p => p.name === patient.insurance_provider);
          coverageRate = provider ? provider.avg_reimbursement_rate : 0.75;
          
          // Add some variation
          coverageRate = Math.max(0.5, Math.min(0.95, coverageRate * (0.9 + Math.random() * 0.2)));
          insuranceCovered = Math.round(chargedAmount * coverageRate);
        }
        
        // Patient responsibility
        const patientResponsibility = chargedAmount - insuranceCovered;
        
        // Discount (15% chance)
        const hasDiscount = Math.random() < 0.15;
        const discountRate = hasDiscount ? (randomBetween(1, 3)) / 10 : 0; // 10%, 20%, or 30% discount
        const discountAmount = Math.round(patientResponsibility * discountRate);
        
        // Final out of pocket
        const outOfPocket = patientResponsibility - discountAmount;
        
        // Payment info
        const isPaid = Math.random() < 0.95; // 95% of procedures are paid
        const amountPaid = isPaid ? outOfPocket : 0;
        const paymentMethod = isPaid ? paymentMethods[Math.floor(Math.random() * paymentMethods.length)] : '';
        
        // Generate a tooth number if applicable
        const needsTooth = ['Restorative', 'Endodontic', 'Periodontic', 'Implant'].includes(procedure.category);
        const toothNumber = needsTooth ? teeth[Math.floor(Math.random() * teeth.length)] : '';
        
        // Treatment plan data (30% chance)
        const hasTreatmentPlan = Math.random() < 0.3;
        let treatmentPlanId = '';
        let treatmentPlanCreationDate = '';
        let treatmentPlanCompletionDate = '';
        let treatmentPlanCompletionRate = 0;
        let estimatedTotalCost = chargedAmount;
        
        if (hasTreatmentPlan) {
          treatmentPlanId = `TP${String(Math.floor(Math.random() * 10000)).padStart(4, '0')}`;
          
          // Create creation date before visit (up to 90 days before)
          const tpCreationDate = new Date(visitDate);
          tpCreationDate.setDate(tpCreationDate.getDate() - randomBetween(0, 90));
          treatmentPlanCreationDate = formatDate(tpCreationDate);
          
          // Determine if treatment plan is completed
          const isCompleted = Math.random() < 0.6; // 60% of treatment plans are completed
          
          if (isCompleted) {
            // Completion date after visit (up to 180 days after)
            const tpCompletionDate = new Date(visitDate);
            tpCompletionDate.setDate(tpCompletionDate.getDate() + randomBetween(0, 180));
            treatmentPlanCompletionDate = formatDate(tpCompletionDate);
            treatmentPlanCompletionRate = 100;
          } else {
            treatmentPlanCompletionRate = randomBetween(10, 90);
          }
          
          // Estimated total cost (with some variation from actual)
          estimatedTotalCost = Math.round(chargedAmount * (1 + Math.random()));
        }
        
        // Claim information
        const claimStatus = hasInsurance ? 
            (Math.random() < 0.95 ? 'Paid' : (Math.random() < 0.5 ? 'Pending' : 'Denied')) : '';
        const claimSubmissionDate = hasInsurance ? formattedVisitDate : '';
        
        let claimPaymentDate = '';
        if (claimStatus === 'Paid') {
            // Payment typically comes 15-45 days after submission
            const paymentDateObj = new Date(visitDate);
            paymentDateObj.setDate(paymentDateObj.getDate() + randomBetween(15, 45));
            claimPaymentDate = formatDate(paymentDateObj);
        }
        
        // Add to appointments array
        appointments.push({
          Visit_ID: visitId,
          Procedure_ID: procedureId,
          Patient_ID: patient.patient_id,
          Patient_Name: patient.name,
          Patient_Gender: patient.gender,
          Patient_Age: patient.age,
          Patient_Zip_Code: patient.zip_code,
          Location_ID: location.id,
          Location_Name: location.name,
          Provider_ID: provider.id,
          Provider_Name: provider.name,
          Provider_Role: provider.role,
          Provider_Specialty: provider.specialty,
          Date_of_Service: formattedVisitDate,
          Appointment_Status: appointmentStatus,
          Procedure_Code: procedure.code,
          Procedure_Description: procedure.description,
          Procedure_Category: procedure.category,
          Tooth_Number: toothNumber,
          Charged_Amount: chargedAmount,
          Insurance_Provider: patient.insurance_provider,
          Insurance_Covered_Amount: insuranceCovered,
          Patient_Responsibility: patientResponsibility,
          Discount_Applied: discountAmount,
          Out_of_Pocket: outOfPocket,
          Amount_Paid: amountPaid,
          Payment_Method: paymentMethod,
          Payment_Status: isPaid ? 'Paid' : 'Outstanding',
          Is_New_Patient: new Date(patient.registration_date).toISOString().split('T')[0] === formattedVisitDate,
          Insurance_Claim_Status: claimStatus,
          Insurance_Claim_Submission_Date: claimSubmissionDate,
          Insurance_Claim_Payment_Date: claimPaymentDate,
          Google_Rating: location.google_rating,
          Treatment_Plan_ID: treatmentPlanId,
          Treatment_Plan_Creation_Date: treatmentPlanCreationDate,
          Treatment_Plan_Completion_Date: treatmentPlanCompletionDate,
          Treatment_Plan_Completion_Rate: treatmentPlanCompletionRate,
          Estimated_Total_Cost: estimatedTotalCost,
          Year: year,
          Month: month
        });
      } else {
        // For non-completed appointments, we still add basic info without financial data
        appointments.push({
          Visit_ID: visitId,
          Procedure_ID: procedureId,
          Patient_ID: patient.patient_id,
          Patient_Name: patient.name,
          Patient_Gender: patient.gender,
          Patient_Age: patient.age,
          Patient_Zip_Code: patient.zip_code,
          Location_ID: location.id,
          Location_Name: location.name,
          Provider_ID: provider.id,
          Provider_Name: provider.name,
          Provider_Role: provider.role,
          Provider_Specialty: provider.specialty,
          Date_of_Service: formattedVisitDate,
          Appointment_Status: appointmentStatus,
          Procedure_Code: '',
          Procedure_Description: '',
          Procedure_Category: '',
          Tooth_Number: '',
          Charged_Amount: 0,
          Insurance_Provider: patient.insurance_provider,
          Insurance_Covered_Amount: 0,
          Patient_Responsibility: 0,
          Discount_Applied: 0,
          Out_of_Pocket: 0,
          Amount_Paid: 0,
          Payment_Method: '',
          Payment_Status: '',
          Is_New_Patient: new Date(patient.registration_date).toISOString().split('T')[0] === formattedVisitDate,
          Insurance_Claim_Status: '',
          Insurance_Claim_Submission_Date: '',
          Insurance_Claim_Payment_Date: '',
          Google_Rating: location.google_rating,
          Treatment_Plan_ID: '',
          Treatment_Plan_Creation_Date: '',
          Treatment_Plan_Completion_Date: '',
          Treatment_Plan_Completion_Rate: 0,
          Estimated_Total_Cost: 0,
          Year: year,
          Month: month
        });
      }
    }
  }
  
  // Sort appointments by date
  appointments.sort((a, b) => {
    return new Date(a.Date_of_Service) - new Date(b.Date_of_Service);
  });
  
  return appointments;
}

// Generate the datasets
const patients = generatePatients();
const appointments = generateAppointmentData(patients);

// Convert arrays to CSV
function convertToCSV(data) {
  // Get headers
  const headers = Object.keys(data[0]);
  
  // Create CSV rows
  const csvRows = [];
  
  // Add headers row
  csvRows.push(headers.join(','));
  
  // Add data rows
  for (const row of data) {
    const values = headers.map(header => {
      const value = row[header];
      // Handle string values that might contain commas
      return typeof value === 'string' ? `"${value}"` : value;
    });
    csvRows.push(values.join(','));
  }
  
  return csvRows.join('\n');
}

// Save datasets to CSV files
const appointmentsCSV = convertToCSV(appointments);
fs.writeFileSync('Dental_Data_Expanded.csv', appointmentsCSV);

console.log(`Created ${appointments.length} dental appointment records`);
console.log(`Data saved to 'Dental_Data_Expanded.csv'`);

// Calculate some metrics for verification
const totalCharged = appointments.reduce((sum, a) => sum + (a.Charged_Amount || 0), 0);
const totalCollected = appointments.reduce((sum, a) => sum + (a.Amount_Paid || 0), 0);
console.log(`Total charged: $${totalCharged.toLocaleString()}`);
console.log(`Total collected: $${totalCollected.toLocaleString()}`);
console.log(`Collection rate: ${(totalCollected / totalCharged * 100).toFixed(2)}%`);

// Count records by year
const byYear = {};
appointments.forEach(a => {
  byYear[a.Year] = (byYear[a.Year] || 0) + 1;
});
console.log("Records by year:", byYear);

// Count unique patients, locations, and providers
const uniquePatients = new Set(appointments.map(a => a.Patient_ID)).size;
const uniqueLocations = new Set(appointments.map(a => a.Location_ID)).size;
const uniqueProviders = new Set(appointments.map(a => a.Provider_ID)).size;
console.log(`Number of unique patients: ${uniquePatients}`);
console.log(`Number of unique locations: ${uniqueLocations}`);
console.log(`Number of unique providers: ${uniqueProviders}`);