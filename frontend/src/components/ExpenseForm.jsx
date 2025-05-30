import React, { useState } from 'react';

// ExpenseForm now accepts an onAddExpense prop (a function from parent)
const ExpenseForm = ({ onAddExpense }) => {
    const [expenseData, setExpenseData] = useState({
        amount: '',
        category: '',
        description: '',
        expense_date: ''
    });

    const handleChange = (e) => {
        setExpenseData({ ...expenseData, [e.target.name]: e.target.value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Call the prop function passed from the parent (Home.jsx)
        onAddExpense(expenseData);
        // Clear form after submission
        setExpenseData({
            amount: '',
            category: '',
            description: '',
            expense_date: ''
        });
    };

    return (
        <div style={{ padding: '10px' }}>
            <h2>Add Expense</h2>
            <form onSubmit={handleSubmit}>
                {/* User ID input removed as it's handled by parent now */}
                <div>
                    <label>Amount:</label>
                    <input type="number" name="amount" step="0.01" value={expenseData.amount} onChange={handleChange} required />
                </div>
                <div>
                    <label>Category:</label>
                    <input type="text" name="category" value={expenseData.category} onChange={handleChange} required />
                </div>
                <div>
                    <label>Description:</label>
                    <input type="text" name="description" value={expenseData.description} onChange={handleChange} />
                </div>
                <div>
                    <label>Expense Date:</label>
                    <input type="date" name="expense_date" value={expenseData.expense_date} onChange={handleChange} required />
                </div>
                <button type="submit">Add Expense</button>
            </form>
        </div>
    );
};

export default ExpenseForm;
