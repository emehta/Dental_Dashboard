// Dental Practice Financial Dataset Generator for CFO Analytics
// This script creates a realistic financial dataset spanning 2020 to 2025
// Focus on base-level financial data for multi-site dental practices

const fs = require('fs');

// Helper functions
function randomBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

function randomFloatBetween(min, max, precision = 2) {
  const value = Math.random() * (max - min) + min;
  const multiplier = Math.pow(10, precision);
  return Math.round(value * multiplier) / multiplier;
}

function formatDate(date) {
  return date.toISOString().split('T')[0];
}

// Constants
const START_DATE = new Date(2020, 0, 1); // Jan 1, 2020
const END_DATE = new Date(2025, 3, 1);   // Apr 1, 2025

// Locations data
const locations = [
  { 
    id: 'LOC001', 
    name: 'Downtown Dental', 
    address: '123 Main St, Portland, OR 97201',
    opened_date: '2015-03-15',
    square_footage: 3200,
    monthly_rent: 12800,
    acquisition_cost: 850000,
    acquisition_date: '2015-01-15'
  },
  { 
    id: 'LOC002', 
    name: 'Westside Smile Center', 
    address: '456 Park Ave, Portland, OR 97229',
    opened_date: '2017-06-22',
    square_footage: 2800,
    monthly_rent: 9800,
    acquisition_cost: 720000,
    acquisition_date: '2017-04-10'
  },
  { 
    id: 'LOC003', 
    name: 'East Valley Dental Care', 
    address: '789 River Rd, Gresham, OR 97030',
    opened_date: '2019-11-10',
    square_footage: 2400,
    monthly_rent: 7200,
    acquisition_cost: 650000,
    acquisition_date: '2019-09-05'
  }
];

// Service categories for revenue breakdowns
const serviceCategories = [
  'Diagnostic',
  'Preventive',
  'Restorative',
  'Endodontic',
  'Periodontic',
  'Prosthodontic',
  'Oral Surgery',
  'Orthodontic',
  'Implant',
  'Adjunctive'
];

// Insurance providers for payor mix
const insuranceProviders = [
  { name: 'Delta Dental', reimbursement_rate: 0.85 },
  { name: 'Cigna Dental', reimbursement_rate: 0.80 },
  { name: 'Aetna', reimbursement_rate: 0.75 },
  { name: 'MetLife', reimbursement_rate: 0.82 },
  { name: 'Guardian', reimbursement_rate: 0.78 },
  { name: 'United Healthcare', reimbursement_rate: 0.79 },
  { name: 'Self-Pay', reimbursement_rate: 1.00 }
];

// Expense categories
const expenseCategories = [
  'Labor - Clinical',
  'Labor - Administrative',
  'Supplies - Clinical',
  'Supplies - Office',
  'Rent/Lease',
  'Utilities',
  'Equipment Costs',
  'Marketing',
  'Insurance',
  'Professional Fees',
  'Continuing Education',
  'Lab Fees',
  'Software & IT',
  'Travel',
  'Miscellaneous'
];

// Generate seasonal and growth factors
function getSeasonalFactor(date) {
  const month = date.getMonth();
  
  // Winter - slightly slower
  if (month === 11 || month === 0 || month === 1) {
    return randomFloatBetween(0.85, 0.95);
  }
  
  // Spring - busy season
  if (month >= 2 && month <= 4) {
    return randomFloatBetween(1.05, 1.15);
  }
  
  // Summer - mixed
  if (month >= 5 && month <= 7) {
    return randomFloatBetween(0.9, 1.1);
  }
  
  // Fall - moderately busy
  return randomFloatBetween(0.95, 1.05);
}

function getGrowthFactor(date, location) {
  // Calculate years since location opened
  const locationOpenDate = new Date(location.opened_date);
  const yearsSinceOpening = date.getFullYear() - locationOpenDate.getFullYear() + 
                           (date.getMonth() - locationOpenDate.getMonth()) / 12;
  
  // Growth curve - faster growth in early years, then stabilizing
  // Start with baseline
  let baseGrowth = 1.0;
  
  // Clinics less than 2 years old grow at 15-25% annually
  if (yearsSinceOpening < 2) {
    baseGrowth += (yearsSinceOpening * 0.2) * randomFloatBetween(0.9, 1.1);
  } 
  // Clinics 2-4 years old grow at 8-15% annually
  else if (yearsSinceOpening < 4) {
    baseGrowth += 0.4 + ((yearsSinceOpening - 2) * 0.12) * randomFloatBetween(0.9, 1.1);
  } 
  // Clinics 4+ years old grow at 3-8% annually
  else {
    baseGrowth += 0.64 + ((yearsSinceOpening - 4) * 0.055) * randomFloatBetween(0.9, 1.1);
  }
  
  return baseGrowth;
}

// Generate monthly financial data for a specific location and month
function generateMonthlyFinancialData(date, location) {
  const formattedDate = formatDate(date);
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  
  // Calculate seasonal and growth factors
  const seasonalFactor = getSeasonalFactor(date);
  const growthFactor = getGrowthFactor(date, location);
  
  // Get comparative periods
  const lastMonthDate = new Date(date);
  lastMonthDate.setMonth(date.getMonth() - 1);
  const lastYearDate = new Date(date);
  lastYearDate.setFullYear(date.getFullYear() - 1);
  
  // ------ Generate Revenue Data -------
  
  // Base revenue - varies by location size with some randomness
  let baseRevenue = 0;
  if (location.id === 'LOC001') { // Largest location
    baseRevenue = randomBetween(180000, 220000);
  } else if (location.id === 'LOC002') {
    baseRevenue = randomBetween(140000, 170000);
  } else {
    baseRevenue = randomBetween(100000, 130000);
  }
  
  // Apply seasonal and growth factors
  const totalRevenue = Math.round(baseRevenue * seasonalFactor * growthFactor);
  
  // Revenue breakdown by service category
  const serviceRevenue = {};
  const categoryWeights = {
    'Diagnostic': 0.10,
    'Preventive': 0.20,
    'Restorative': 0.25,
    'Endodontic': 0.08,
    'Periodontic': 0.07,
    'Prosthodontic': 0.10,
    'Oral Surgery': 0.05,
    'Orthodontic': 0.08,
    'Implant': 0.05,
    'Adjunctive': 0.02
  };
  
  // Add some randomness to the category weights
  let totalWeight = 0;
  for (const category of serviceCategories) {
    serviceRevenue[category] = categoryWeights[category] * randomFloatBetween(0.85, 1.15);
    totalWeight += serviceRevenue[category];
  }
  
  // Normalize and calculate actual amounts
  for (const category of serviceCategories) {
    serviceRevenue[category] = Math.round((serviceRevenue[category] / totalWeight) * totalRevenue);
  }
  
  // ------ Generate Expense Data -------
  
  // Base expense categories
  const expenseData = {};
  
  // Labor - typically 24-32% of revenue
  expenseData['Labor - Clinical'] = Math.round(totalRevenue * randomFloatBetween(0.18, 0.22));
  expenseData['Labor - Administrative'] = Math.round(totalRevenue * randomFloatBetween(0.06, 0.10));
  
  // Supplies - typically 6-10% of revenue
  expenseData['Supplies - Clinical'] = Math.round(totalRevenue * randomFloatBetween(0.05, 0.08));
  expenseData['Supplies - Office'] = Math.round(totalRevenue * randomFloatBetween(0.01, 0.02));
  
  // Rent - fixed monthly cost but varies slightly
  expenseData['Rent/Lease'] = Math.round(location.monthly_rent * randomFloatBetween(0.98, 1.02));
  
  // Utilities - 1-3% of revenue
  expenseData['Utilities'] = Math.round(totalRevenue * randomFloatBetween(0.01, 0.03));
  
  // Equipment costs - typically 3-5% of revenue (includes lease payments, repairs)
  expenseData['Equipment Costs'] = Math.round(totalRevenue * randomFloatBetween(0.03, 0.05));
  
  // Marketing - 3-7% of revenue
  expenseData['Marketing'] = Math.round(totalRevenue * randomFloatBetween(0.03, 0.07));
  
  // Insurance - 2-4% of revenue
  expenseData['Insurance'] = Math.round(totalRevenue * randomFloatBetween(0.02, 0.04));
  
  // Professional fees - 2-4% of revenue (accounting, legal, consulting)
  expenseData['Professional Fees'] = Math.round(totalRevenue * randomFloatBetween(0.02, 0.04));
  
  // Continuing education - 0.5-1.5% of revenue
  expenseData['Continuing Education'] = Math.round(totalRevenue * randomFloatBetween(0.005, 0.015));
  
  // Lab fees - 6-10% of revenue
  expenseData['Lab Fees'] = Math.round(totalRevenue * randomFloatBetween(0.06, 0.10));
  
  // Software & IT - 1-3% of revenue
  expenseData['Software & IT'] = Math.round(totalRevenue * randomFloatBetween(0.01, 0.03));
  
  // Travel - 0.5-1.5% of revenue
  expenseData['Travel'] = Math.round(totalRevenue * randomFloatBetween(0.005, 0.015));
  
  // Miscellaneous - 1-3% of revenue
  expenseData['Miscellaneous'] = Math.round(totalRevenue * randomFloatBetween(0.01, 0.03));
  
  // Calculate total expenses
  const totalExpenses = Object.values(expenseData).reduce((sum, value) => sum + value, 0);
  
  // ------ Generate Cash Flow Data -------
  
  // Accounts receivable - 30-45 days of revenue
  const daysInAR = randomBetween(30, 45);
  const accountsReceivable = Math.round(totalRevenue * (daysInAR / 30));
  
  // AR aging buckets
  const arAging = {
    'Current': Math.round(accountsReceivable * randomFloatBetween(0.55, 0.65)),
    '31-60 Days': Math.round(accountsReceivable * randomFloatBetween(0.20, 0.25)),
    '61-90 Days': Math.round(accountsReceivable * randomFloatBetween(0.08, 0.12)),
    '91+ Days': Math.round(accountsReceivable * randomFloatBetween(0.05, 0.10))
  };
  
  // Insurance claims data
  const totalClaims = Math.round(totalRevenue * 0.8 / 150); // Estimate number of claims based on avg claim of $150
  const claimsSubmitted = totalClaims;
  const claimsOutstanding = Math.round(totalClaims * randomFloatBetween(0.3, 0.4));
  const claimsDenied = Math.round(totalClaims * randomFloatBetween(0.02, 0.05));
  const avgDaysToPayment = randomBetween(25, 40);
  
  // Payment collection data
  const collectionsExpected = totalRevenue * 0.9; // Expected to collect 90% of revenue
  const collectionsActual = collectionsExpected * randomFloatBetween(0.88, 0.99);
  const collectionRate = collectionsActual / totalRevenue;
  
  // Procedure data
  const numberOfProcedures = Math.round(totalRevenue / randomBetween(200, 300)); // Average procedure value
  const completedProcedures = Math.round(numberOfProcedures * randomFloatBetween(0.92, 0.98));
  const cancelledProcedures = Math.round(numberOfProcedures * randomFloatBetween(0.02, 0.08));
  
  // Patient data
  const patientVisits = Math.round(numberOfProcedures * 0.7); // Some patients get multiple procedures
  const newPatients = Math.round(patientVisits * randomFloatBetween(0.15, 0.25));
  const returningPatients = patientVisits - newPatients;
  const patientRetentionRate = randomFloatBetween(0.75, 0.9);
  
  // Capacity and utilization
  const chairCapacity = location.id === 'LOC001' ? 5 : (location.id === 'LOC002' ? 4 : 3);
  const operatingDays = 22; // Average business days in month
  const operatingHours = 8; // Hours per day
  const totalChairHours = chairCapacity * operatingDays * operatingHours;
  const usedChairHours = totalChairHours * randomFloatBetween(0.7, 0.9);
  
  // Payor mix - distribution of revenue by insurance provider
  const payorMix = {};
  const payorWeights = {
    'Delta Dental': 0.30,
    'Cigna Dental': 0.15,
    'Aetna': 0.12,
    'MetLife': 0.10,
    'Guardian': 0.08,
    'United Healthcare': 0.05,
    'Self-Pay': 0.20
  };
  
  // Add some randomness to the payor weights
  let totalPayorWeight = 0;
  for (const provider of insuranceProviders) {
    const weight = payorWeights[provider.name] || 0.02;
    payorMix[provider.name] = weight * randomFloatBetween(0.85, 1.15);
    totalPayorWeight += payorMix[provider.name];
  }
  
  // Normalize and calculate actual amounts
  for (const provider of insuranceProviders) {
    payorMix[provider.name] = Math.round((payorMix[provider.name] / totalPayorWeight) * totalRevenue);
  }
  
  // Treatment acceptance and completion rates
  const treatmentPlansPresented = Math.round(patientVisits * randomFloatBetween(0.3, 0.5));
  const treatmentPlansAccepted = Math.round(treatmentPlansPresented * randomFloatBetween(0.6, 0.8));
  const treatmentPlansCompleted = Math.round(treatmentPlansAccepted * randomFloatBetween(0.7, 0.9));
  
  // Generate KPIs and ratios
  const ebitda = totalRevenue - totalExpenses;
  const ebitdaMargin = ebitda / totalRevenue;
  const operatingCashFlow = collectionsActual - totalExpenses;
  const dso = accountsReceivable / (totalRevenue / 30); // Days Sales Outstanding
  const revenuePerSquareFoot = totalRevenue / location.square_footage;
  const revenuePerPatient = totalRevenue / patientVisits;
  const marketingROI = (totalRevenue * 0.15) / expenseData['Marketing']; // Assume 15% of revenue from marketing
  
  // Generate main financial record
  return {
    Financial_ID: `FIN-${location.id}-${year}${String(month).padStart(2, '0')}`,
    Location_ID: location.id,
    Location_Name: location.name,
    Date: formattedDate,
    Year: year,
    Month: month,
    Period: `${year}-${String(month).padStart(2, '0')}`,
    
    // Revenue metrics
    Total_Revenue: totalRevenue,
    Revenue_Diagnostic: serviceRevenue['Diagnostic'],
    Revenue_Preventive: serviceRevenue['Preventive'],
    Revenue_Restorative: serviceRevenue['Restorative'],
    Revenue_Endodontic: serviceRevenue['Endodontic'],
    Revenue_Periodontic: serviceRevenue['Periodontic'],
    Revenue_Prosthodontic: serviceRevenue['Prosthodontic'],
    Revenue_Oral_Surgery: serviceRevenue['Oral Surgery'],
    Revenue_Orthodontic: serviceRevenue['Orthodontic'],
    Revenue_Implant: serviceRevenue['Implant'],
    Revenue_Adjunctive: serviceRevenue['Adjunctive'],
    
    // Expense metrics
    Total_Expenses: totalExpenses,
    Labor_Clinical: expenseData['Labor - Clinical'],
    Labor_Administrative: expenseData['Labor - Administrative'],
    Supplies_Clinical: expenseData['Supplies - Clinical'],
    Supplies_Office: expenseData['Supplies - Office'],
    Rent_Lease: expenseData['Rent/Lease'],
    Utilities: expenseData['Utilities'],
    Equipment_Costs: expenseData['Equipment Costs'],
    Marketing: expenseData['Marketing'],
    Insurance: expenseData['Insurance'],
    Professional_Fees: expenseData['Professional Fees'],
    Continuing_Education: expenseData['Continuing Education'],
    Lab_Fees: expenseData['Lab Fees'],
    Software_IT: expenseData['Software & IT'],
    Travel: expenseData['Travel'],
    Miscellaneous: expenseData['Miscellaneous'],
    
    // Profitability metrics
    EBITDA: ebitda,
    EBITDA_Margin: ebitdaMargin.toFixed(4),
    Labor_Cost_Percentage: ((expenseData['Labor - Clinical'] + expenseData['Labor - Administrative']) / totalRevenue).toFixed(4),
    Supply_Cost_Percentage: ((expenseData['Supplies - Clinical'] + expenseData['Supplies - Office']) / totalRevenue).toFixed(4),
    
    // Accounts receivable
    Total_AR: accountsReceivable,
    AR_Current: arAging['Current'],
    AR_31_60: arAging['31-60 Days'],
    AR_61_90: arAging['61-90 Days'],
    AR_91_Plus: arAging['91+ Days'],
    DSO: dso.toFixed(1),
    
    // Insurance claims
    Total_Claims_Submitted: claimsSubmitted,
    Claims_Outstanding: claimsOutstanding,
    Claims_Denied: claimsDenied,
    Avg_Days_To_Payment: avgDaysToPayment,
    
    // Collections
    Collections_Expected: Math.round(collectionsExpected),
    Collections_Actual: Math.round(collectionsActual),
    Collection_Rate: collectionRate.toFixed(4),
    
    // Procedure metrics
    Total_Procedures: numberOfProcedures,
    Completed_Procedures: completedProcedures,
    Cancelled_Procedures: cancelledProcedures,
    
    // Patient metrics
    Total_Patient_Visits: patientVisits,
    New_Patients: newPatients,
    Returning_Patients: returningPatients,
    Patient_Retention_Rate: patientRetentionRate.toFixed(4),
    Revenue_Per_Patient: revenuePerPatient.toFixed(2),
    
    // Capacity metrics
    Chair_Capacity: chairCapacity,
    Total_Chair_Hours: totalChairHours,
    Used_Chair_Hours: Math.round(usedChairHours),
    Chair_Utilization: (usedChairHours / totalChairHours).toFixed(4),
    
    // Payor mix
    Payor_Delta_Dental: payorMix['Delta Dental'],
    Payor_Cigna_Dental: payorMix['Cigna Dental'],
    Payor_Aetna: payorMix['Aetna'],
    Payor_MetLife: payorMix['MetLife'],
    Payor_Guardian: payorMix['Guardian'],
    Payor_United_Healthcare: payorMix['United Healthcare'],
    Payor_Self_Pay: payorMix['Self-Pay'],
    
    // Treatment plan metrics
    Treatment_Plans_Presented: treatmentPlansPresented,
    Treatment_Plans_Accepted: treatmentPlansAccepted,
    Treatment_Plans_Completed: treatmentPlansCompleted,
    Case_Acceptance_Rate: (treatmentPlansAccepted / treatmentPlansPresented).toFixed(4),
    Treatment_Completion_Rate: (treatmentPlansCompleted / treatmentPlansAccepted).toFixed(4),
    
    // PE/CFO specific metrics
    Revenue_Per_Square_Foot: revenuePerSquareFoot.toFixed(2),
    Marketing_ROI: marketingROI.toFixed(2),
    Operating_Cash_Flow: operatingCashFlow,
    
    // Comparative metrics
    Revenue_MoM_Change: 0, // Will be filled in later
    Revenue_YoY_Change: 0, // Will be filled in later
    EBITDA_MoM_Change: 0,  // Will be filled in later
    EBITDA_YoY_Change: 0   // Will be filled in later
  };
}

// Function to generate the entire dataset
function generateFinancialDataset() {
  const financialData = [];
  
  // Generate monthly records for each location
  for (const location of locations) {
    // Get start date for this location (either global start date or location opening date, whichever is later)
    const locationOpenDate = new Date(location.opened_date);
    const startDate = locationOpenDate > START_DATE ? new Date(locationOpenDate) : new Date(START_DATE);
    
    // Set to first day of the month
    startDate.setDate(1);
    
    // Generate data for each month
    let currentDate = new Date(startDate);
    
    while (currentDate <= END_DATE) {
      const monthData = generateMonthlyFinancialData(currentDate, location);
      financialData.push(monthData);
      
      // Move to next month
      currentDate.setMonth(currentDate.getMonth() + 1);
    }
  }
  
  // Sort by location and date
  financialData.sort((a, b) => {
    if (a.Location_ID === b.Location_ID) {
      return new Date(a.Date) - new Date(b.Date);
    }
    return a.Location_ID.localeCompare(b.Location_ID);
  });
  
  // Calculate comparative metrics (MoM and YoY changes)
  for (let i = 0; i < financialData.length; i++) {
    const current = financialData[i];
    
    // Find previous month record (same location)
    const prevMonth = financialData.find(item => 
      item.Location_ID === current.Location_ID && 
      item.Year === (current.Month === 1 ? current.Year - 1 : current.Year) && 
      item.Month === (current.Month === 1 ? 12 : current.Month - 1)
    );
    
    // Find previous year record (same location, same month)
    const prevYear = financialData.find(item => 
      item.Location_ID === current.Location_ID && 
      item.Year === current.Year - 1 && 
      item.Month === current.Month
    );
    
    // Calculate MoM changes
    if (prevMonth) {
      current.Revenue_MoM_Change = ((current.Total_Revenue - prevMonth.Total_Revenue) / prevMonth.Total_Revenue).toFixed(4);
      current.EBITDA_MoM_Change = ((current.EBITDA - prevMonth.EBITDA) / prevMonth.EBITDA).toFixed(4);
    }
    
    // Calculate YoY changes
    if (prevYear) {
      current.Revenue_YoY_Change = ((current.Total_Revenue - prevYear.Total_Revenue) / prevYear.Total_Revenue).toFixed(4);
      current.EBITDA_YoY_Change = ((current.EBITDA - prevYear.EBITDA) / prevYear.EBITDA).toFixed(4);
    }
  }
  
  return financialData;
}

// Generate the dataset
const financialDataset = generateFinancialDataset();

// Convert array to CSV
function convertToCSV(data) {
  // Skip empty datasets
  if (!data || data.length === 0) return '';
  
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

// Save dataset to CSV file
const financialCSV = convertToCSV(financialDataset);
fs.writeFileSync('Dental_Financial_Data.csv', financialCSV);

// Log results
console.log(`Generated ${financialDataset.length} financial records`);
console.log('Data saved to "Dental_Financial_Data.csv"');

// Calculate some metrics for verification
const totalRevenue = financialDataset.reduce((sum, record) => sum + record.Total_Revenue, 0);
const totalEBITDA = financialDataset.reduce((sum, record) => sum + record.EBITDA, 0);
const avgMargin = totalEBITDA / totalRevenue;

console.log(`Total Revenue: $${totalRevenue.toLocaleString()}`);
console.log(`Total EBITDA: $${totalEBITDA.toLocaleString()}`);
console.log(`Average EBITDA Margin: ${(avgMargin * 100).toFixed(2)}%`);

// Count records by year
const byYear = {};
financialDataset.forEach(record => {
  byYear[record.Year] = (byYear[record.Year] || 0) + 1;
});
console.log("Records by year:", byYear);

// Count records by location
const byLocation = {};
financialDataset.forEach(record => {
  byLocation[record.Location_Name] = (byLocation[record.Location_Name] || 0) + 1;
});
console.log("Records by location:", byLocation);