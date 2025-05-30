import React, { useState } from 'react';

// BudgetForm now accepts an onSetBudget prop (a function from parent)
const BudgetForm = ({ onSetBudget }) => {
    const [budgetData, setBudgetData] = useState({
        category: '',
        amount: '',
        start_date: '',
        end_date: ''
    });

    const handleChange = (e) => {
        setBudgetData({ ...budgetData, [e.target.name]: e.target.value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Call the prop function passed from the parent (Home.jsx)
        onSetBudget(budgetData);
        // Clear form after submission
        setBudgetData({
            category: '',
            amount: '',
            start_date: '',
            end_date: ''
        });
    };

    return (
        <div style={{ padding: '10px' }}>
            <h2>Set Budget</h2>
            <form onSubmit={handleSubmit}>
                {/* User ID input removed as it's handled by parent now */}
                <div>
                    <label>Category:</label>
                    <input type="text" name="category" value={budgetData.category} onChange={handleChange} required />
                </div>
                <div>
                    <label>Amount:</label>
                    <input type="number" name="amount" step="0.01" value={budgetData.amount} onChange={handleChange} required />
                </div>
                <div>
                    <label>Start Date:</label>
                    <input type="date" name="start_date" value={budgetData.start_date} onChange={handleChange} required />
                </div>
                <div>
                    <label>End Date:</label>
                    <input type="date" name="end_date" value={budgetData.end_date} onChange={handleChange} required />
                </div>
                <button type="submit">Set Budget</button>
            </form>
        </div>
    );
};

export default BudgetForm;
