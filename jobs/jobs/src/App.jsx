import React, { useState } from 'react';

// Sample job data (replace this with your real data fetching logic if needed)
const jobData = {
  message: "Success",
  results: [
    {
      Company: "Fluid Robotics",
      Date_Posted: "19 hours ago",
      Employment_Type: "Full-time",
      First_Job_Provider_URL: "https://watertechjobs.imagineh2o.org/companies/fluid-robotics/jobs/41157551-machine-learning-engineer-computer-vision",
      Keyword_Matched: "machine learning"
    },
    {
      Company: "LearnTube.ai (backed by Google)",
      Date_Posted: "1 month ago",
      Employment_Type: "Full-time and Internship",
      First_Job_Provider_URL: "https://wellfound.com/jobs/2758614-generative-ai-machine-learning-intern",
      Keyword_Matched: "machine learning"
    },
    {
      Company: "Prodigal",
      Date_Posted: "1 month ago",
      Employment_Type: "Full-time",
      First_Job_Provider_URL: "https://boards.greenhouse.io/prodigal/jobs/4510383007",
      Keyword_Matched: "machine learning"
    },
    {
      Company: "Zycus",
      Date_Posted: "",
      Employment_Type: "Full-time",
      First_Job_Provider_URL: "https://zycus.sensehq.com/careers/jobs/54016",
      Keyword_Matched: "machine learning"
    },
    {
      Company: "Wipro",
      Date_Posted: "",
      Employment_Type: "Full-time",
      First_Job_Provider_URL: "https://careers.wipro.com/opportunities/jobs/3097523",
      Keyword_Matched: "AI"
    }
  ]
};

export default function JobSearch() {
  const [searchTerm, setSearchTerm] = useState('');

  // Filter jobs based on search term (case insensitive)
  const filteredJobs = jobData.results.filter(job =>
    Object.values(job).some(value =>
      value.toString().toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div style={styles.outerContainer}>
      <h1 style={styles.title}>Job Search Portal</h1>
      <div style={styles.container}>
        <input
          type="text"
          placeholder="Search jobs by company, type, or keyword..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={styles.searchBar}
        />

        <div style={styles.gridContainer}>
          {filteredJobs.length > 0 ? (
            filteredJobs.map((job, index) => (
              <div key={index} style={styles.card}>
                <h3 style={styles.company}>{job.Company}</h3>
                <p><strong>Type:</strong> {job.Employment_Type}</p>
                {job.Date_Posted && <p><strong>Posted:</strong> {job.Date_Posted}</p>}
                <p><strong>Keyword:</strong> {job.Keyword_Matched}</p>
                <a 
                  href={job.First_Job_Provider_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={styles.applyLink}
                >
                  Apply Now →
                </a>
              </div>
            ))
          ) : (
            <p>No jobs found.</p>
          )}
        </div>
      </div>
    </div>
  );
}

// Inline styles
const styles = {
  outerContainer: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh', // Full height of the viewport
    width: '100vw', // Full width of the viewport
    backgroundColor: '#f0f0f0',
    fontFamily: 'Arial, sans-serif',
    textAlign: 'center',
    padding: '0 20px',
  },
  title: {
    fontSize: '36px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#333',
  },
  container: {
    width: '100%',
    maxWidth: '1200px',
    padding: '20px',
    borderRadius: '10px',
    backgroundColor: '#fff',
    boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.1)',
    textAlign: 'center',
  },
  searchBar: {
    width: '90%',
    padding: '12px 15px',
    marginBottom: '20px',
    fontSize: '16px',
    border: '1px solid #ccc',
    borderRadius: '8px',
    outline: 'none',
  },
  gridContainer: {
    display: 'grid', // Use grid layout
    gridTemplateColumns: 'repeat(3, 1fr)', // Three cards per row
    gap: '20px',
  },
  card: {
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '15px',
    boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.1)',
    transition: 'box-shadow 0.3s ease-in-out',
    backgroundColor: '#fff',
    color: '#000',
  },
  company: {
    marginBottom: '10px',
    fontSize: '20px',
    color: '#333',
  },
  applyLink: {
    color: '#007BFF',
    textDecoration: 'none',
    display: 'inline-block',
    marginTop: '10px',
    fontWeight: 'bold',
  },
};
