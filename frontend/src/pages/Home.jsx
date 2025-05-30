import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChatInterface from '../components/ChatInterface';
import ExpenseForm from '../components/ExpenseForm';
import BudgetForm from '../components/BudgetForm';

const Home = () => {
    const [expenses, setExpenses] = useState([]);
    const [budgets, setBudgets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // Hardcoded user ID for now. In a real app, this would come from authentication.
    const CURRENT_USER_ID = 1; 

    // Base URL for your backend API (adjust if needed)
    const API_BASE_URL = 'http://localhost:5000';

    // Function to fetch and refresh expenses and budgets
    const fetchExpensesAndBudgets = async () => {
        setLoading(true);
        setError(null);
        try {
            const expensesResponse = await axios.get(`${API_BASE_URL}/expenses?user_id=${CURRENT_USER_ID}`);
            setExpenses(expensesResponse.data);

            const budgetsResponse = await axios.get(`${API_BASE_URL}/budgets?user_id=${CURRENT_USER_ID}`);
            setBudgets(budgetsResponse.data);
        } catch (err) {
            setError(err.message || 'Could not fetch data');
            console.error("Error fetching initial data:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchExpensesAndBudgets();
    }, []); // Empty dependency array means this runs only once on component mount

    const handleAddExpense = async (expenseData) => {
        try {
            // Ensure user_id is set for the expense
            const dataToSend = { ...expenseData, user_id: CURRENT_USER_ID };
            const response = await axios.post(`${API_BASE_URL}/expenses`, dataToSend);
            alert('Expense added successfully!');
            fetchExpensesAndBudgets(); // Refresh data after adding
        } catch (err) {
            const errorMessage = err.response?.data?.error || err.message || 'Could not add expense';
            setError(errorMessage);
            alert(`Error adding expense: ${errorMessage}`);
            console.error("Error adding expense:", err);
        }
    };

    const handleSetBudget = async (budgetData) => {
        try {
            // Ensure user_id is set for the budget
            const dataToSend = { ...budgetData, user_id: CURRENT_USER_ID };
            const response = await axios.post(`${API_BASE_URL}/budgets`, dataToSend);
            alert('Budget set successfully!');
            fetchExpensesAndBudgets(); // Refresh data after setting
        } catch (err) {
            const errorMessage = err.response?.data?.error || err.message || 'Could not set budget';
            setError(errorMessage);
            alert(`Error setting budget: ${errorMessage}`);
            console.error("Error setting budget:", err);
        }
    };

    if (loading) {
        return <div>Loading financial data...</div>;
    }

    if (error) {
        return <div style={{color: 'red'}}>Error: {error}</div>;
    }

    return (
        <div style={{ fontFamily: 'sans-serif', margin: '20px' }}>
            <h1 style={{ textAlign: 'center' }}>Personal Finance Chatbot</h1>

            <div style={{ display: 'flex', justifyContent: 'space-around', gap: '20px', flexWrap: 'wrap' }}>
                <div style={{ flex: '1 1 45%', minWidth: '300px', maxWidth: '500px' }}>
                    <ChatInterface userId={CURRENT_USER_ID} />
                </div>
                <div style={{ flex: '1 1 45%', minWidth: '300px', maxWidth: '500px', border: '1px solid #ccc', padding: '10px', borderRadius: '8px' }}>
                    <ExpenseForm onAddExpense={handleAddExpense} />
                </div>
                <div style={{ flex: '1 1 45%', minWidth: '300px', maxWidth: '500px', border: '1px solid #ccc', padding: '10px', borderRadius: '8px' }}>
                    <BudgetForm onSetBudget={handleSetBudget} />
                </div>
            </div>

            <div style={{ marginTop: '30px' }}>
                <h2 style={{ textAlign: 'center' }}>Your Financial Overview (User ID: {CURRENT_USER_ID})</h2>
                <div style={{ display: 'flex', justifyContent: 'space-around', gap: '20px', flexWrap: 'wrap' }}>
                    <div style={{ flex: '1 1 45%', minWidth: '300px', border: '1px solid #ccc', padding: '10px', borderRadius: '8px' }}>
                        <h3>Recent Expenses</h3>
                        {expenses.length > 0 ? (
                            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
                                <thead>
                                    <tr>
                                        <th style={{ border: '1px solid #ccc', padding: '5px', textAlign: 'left', backgroundColor: '#f0f0f0' }}>Amount</th>
                                        <th style={{ border: '1px solid #ccc', padding: '5px', textAlign: 'left', backgroundColor: '#f0f0f0' }}>Category</th>
                                        <th style={{ border: '1px solid #ccc', padding: '5px', textAlign: 'left', backgroundColor: '#f0f0f0' }}>Date</th>
                                        <th style={{ border: '1px solid #ccc', padding: '5px', textAlign: 'left', backgroundColor: '#f0f0f0' }}>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {expenses.map(expense => (
                                        <tr key={expense.expense_id}>
                                            <td style={{ border: '1px solid #ccc', padding: '5px' }}>{expense.amount}</td>
                                            <td style={{ border: '1px solid #ccc', padding: '5px' }}>{expense.category}</td>
                                            <td style={{ border: '1px solid #ccc', padding: '5px' }}>{expense.expense_date}</td>
                                            <td style={{ border: '1px solid #ccc', padding: '5px' }}>{expense.description}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <p>No expenses recorded for this user. Try adding one!</p>
                        )}
                    </div>

                    <div style={{ flex: '1 1 45%', minWidth: '300px', border: '1px solid #ccc', padding: '10px', borderRadius: '8px' }}>
                        <h3>Current Budgets</h3>
                        {budgets.length > 0 ? (
                            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
                                <thead>
                                    <tr>
                                        <th style={{ border: '1px solid #ccc', padding: '5px', textAlign: 'left', backgroundColor: '#f0f0f0' }}>Category</th>
                                        <th style={{ border: '1px solid #ccc', padding: '5px', textAlign: 'left', backgroundColor: '#f0f0f0' }}>Budgeted</th>
                                        <th style={{ border: '1px solid #ccc', padding: '5px', textAlign: 'left', backgroundColor: '#f0f0f0' }}>Spent</th>
                                        <th style={{ border: '1px solid #ccc', padding: '5px', textAlign: 'left', backgroundColor: '#f0f0f0' }}>Remaining</th>
                                        <th style={{ border: '1px solid #ccc', padding: '5px', textAlign: 'left', backgroundColor: '#f0f0f0' }}>Period</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {budgets.map(budget => (
                                        <tr key={budget.category + budget.start_date}> {/* Unique key for budgets */}
                                            <td style={{ border: '1px solid #ccc', padding: '5px' }}>{budget.category}</td>
                                            <td style={{ border: '1px solid #ccc', padding: '5px' }}>{budget.budgeted_amount}</td>
                                            <td style={{ border: '1px solid #ccc', padding: '5px' }}>{budget.actual_spent}</td>
                                            <td style={{ border: '1px solid #ccc', padding: '5px' }}>{budget.remaining_amount}</td>
                                            <td style={{ border: '1px solid #ccc', padding: '5px' }}>{budget.start_date} to {budget.end_date}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <p>No budgets set for this user. Try setting one!</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;
