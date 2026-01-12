import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import '@/App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

function App() {
  const [overview, setOverview] = useState(null);
  const [delays, setDelays] = useState(null);
  const [cancellations, setCancellations] = useState(null);
  const [stockouts, setStockouts] = useState(null);
  const [riders, setRiders] = useState(null);
  const [picking, setPicking] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const [overviewRes, delaysRes, cancellationsRes, stockoutsRes, ridersRes, pickingRes, recsRes] = await Promise.all([
        axios.get(`${API}/analytics/overview`),
        axios.get(`${API}/analytics/order-delays`),
        axios.get(`${API}/analytics/cancellations`),
        axios.get(`${API}/analytics/stockouts`),
        axios.get(`${API}/analytics/riders`),
        axios.get(`${API}/analytics/picking-time`),
        axios.get(`${API}/analytics/recommendations`)
      ]);

      setOverview(overviewRes.data);
      setDelays(delaysRes.data);
      setCancellations(cancellationsRes.data);
      setStockouts(stockoutsRes.data);
      setRiders(ridersRes.data);
      setPicking(pickingRes.data);
      setRecommendations(recsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics data:', error);
      setLoading(false);
    }
  };

  const handleExportExcel = async () => {
    try {
      const response = await axios.get(`${API}/analytics/export-excel`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `quickcommerce_analytics_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error exporting Excel:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-700 font-medium">Loading analytics data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900" data-testid="dashboard-title">Quick Commerce Analytics</h1>
              <p className="text-sm text-gray-600 mt-1">Operations & Customer Experience Analysis</p>
            </div>
            <button
              onClick={handleExportExcel}
              data-testid="export-excel-button"
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export Excel Report
            </button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'overview', name: 'Overview' },
              { id: 'delays', name: 'Order Delays' },
              { id: 'cancellations', name: 'Cancellations' },
              { id: 'stockouts', name: 'Stockouts' },
              { id: 'riders', name: 'Rider Performance' },
              { id: 'picking', name: 'Picking Time' },
              { id: 'recommendations', name: 'Recommendations' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                data-testid={`tab-${tab.id}`}
                className={`${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && <OverviewTab data={overview} />}
        {activeTab === 'delays' && <DelaysTab data={delays} />}
        {activeTab === 'cancellations' && <CancellationsTab data={cancellations} />}
        {activeTab === 'stockouts' && <StockoutsTab data={stockouts} />}
        {activeTab === 'riders' && <RidersTab data={riders} />}
        {activeTab === 'picking' && <PickingTab data={picking} />}
        {activeTab === 'recommendations' && <RecommendationsTab data={recommendations} />}
      </main>
    </div>
  );
}

// Overview Tab Component
function OverviewTab({ data }) {
  if (!data) return null;

  const metrics = [
    { label: 'Total Orders', value: data.total_orders, color: 'bg-blue-500' },
    { label: 'Delivered Orders', value: data.delivered_orders, color: 'bg-green-500' },
    { label: 'Cancelled Orders', value: data.cancelled_orders, color: 'bg-red-500' },
    { label: 'Cancellation Rate', value: `${data.cancellation_rate}%`, color: 'bg-orange-500' },
    { label: 'Avg Delivery Time', value: `${data.avg_delivery_time} min`, color: 'bg-purple-500' },
    { label: 'Avg Delay', value: `${data.avg_delay} min`, color: 'bg-pink-500' },
    { label: 'On-Time Rate', value: `${data.on_time_rate}%`, color: 'bg-teal-500' },
    { label: 'Stockout Rate', value: `${data.stockout_rate}%`, color: 'bg-yellow-500' }
  ];

  return (
    <div data-testid="overview-tab">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Performance Metrics</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200" data-testid={`metric-card-${index}`}>
            <div className={`w-12 h-12 ${metric.color} rounded-lg flex items-center justify-center mb-4`}>
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p className="text-sm text-gray-600 mb-1">{metric.label}</p>
            <p className="text-3xl font-bold text-gray-900">{metric.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// Delays Tab Component
function DelaysTab({ data }) {
  if (!data) return null;

  const delayDistribution = Object.entries(data.delay_distribution || {}).map(([key, value]) => ({
    name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value
  }));

  const zoneData = Object.entries(data.delays_by_zone || {}).map(([zone, stats]) => ({
    zone,
    avgDelay: stats.avg_delay,
    count: stats.count
  }));

  const hourlyData = Object.entries(data.hourly_delays || {}).map(([hour, delay]) => ({
    hour: `${hour}:00`,
    delay
  }));

  return (
    <div data-testid="delays-tab" className="space-y-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Delay Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={delayDistribution}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Average Delay by Zone</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={zoneData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="zone" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="avgDelay" fill="#82ca9d" name="Avg Delay (min)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Hourly Delay Pattern</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={hourlyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="delay" stroke="#ff7300" name="Avg Delay (min)" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// Cancellations Tab Component
function CancellationsTab({ data }) {
  if (!data) return null;

  const reasonData = Object.entries(data.cancellation_reasons || {}).map(([reason, count]) => ({
    name: reason,
    value: count
  }));

  const zoneData = Object.entries(data.cancellations_by_zone || {}).map(([zone, count]) => ({
    zone,
    count
  }));

  return (
    <div data-testid="cancellations-tab" className="space-y-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Cancellation Reasons</h3>
        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
            <Pie
              data={reasonData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={120}
              fill="#8884d8"
              dataKey="value"
            >
              {reasonData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Cancellations by Zone</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={zoneData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="zone" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#ff8042" name="Cancellations" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// Stockouts Tab Component
function StockoutsTab({ data }) {
  if (!data) return null;

  const deptData = Object.entries(data.stockouts_by_department || {}).map(([dept, count]) => ({
    department: dept,
    count
  }));

  return (
    <div data-testid="stockouts-tab" className="space-y-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Top Products with Stockouts</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stockout Count</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {(data.top_stockout_products || []).map((product, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{product.product_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.department}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.stockout_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Stockouts by Department</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={deptData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="department" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#ffc658" name="Stockout Count" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// Riders Tab Component
function RidersTab({ data }) {
  if (!data) return null;

  return (
    <div data-testid="riders-tab" className="space-y-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Top Performing Riders (Low Delay)</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rider</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Zone</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Deliveries</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Delay (min)</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {(data.top_performers || []).map((rider, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{rider.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{rider.zone}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{rider.total_deliveries}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{rider.avg_delay}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Overloaded Riders (High Volume)</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rider</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Zone</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Deliveries</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Delay (min)</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {(data.overloaded_riders || []).map((rider, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{rider.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{rider.zone}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{rider.total_deliveries}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{rider.avg_delay}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// Picking Tab Component
function PickingTab({ data }) {
  if (!data) return null;

  const orderSizeData = (data.picking_time_by_order_size || []).map(item => ({
    items: item.total_items,
    pickingTime: item.avg_picking_time
  }));

  return (
    <div data-testid="picking-tab" className="space-y-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Slowest Stores (Picking Time)</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Store</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Zone</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Picking Time (min)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order Count</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {(data.slowest_stores || []).map((store, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{store.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{store.zone}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{store.avg_picking_time}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{store.order_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Picking Time by Order Size</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={orderSizeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="items" label={{ value: 'Number of Items', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: 'Picking Time (min)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="pickingTime" stroke="#8884d8" name="Avg Picking Time" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// Recommendations Tab Component
function RecommendationsTab({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <p className="text-gray-500">No recommendations available at this time.</p>
      </div>
    );
  }

  const priorityColors = {
    'Critical': 'bg-red-100 text-red-800 border-red-300',
    'High': 'bg-orange-100 text-orange-800 border-orange-300',
    'Medium': 'bg-yellow-100 text-yellow-800 border-yellow-300',
    'Low': 'bg-green-100 text-green-800 border-green-300'
  };

  return (
    <div data-testid="recommendations-tab" className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Data-Driven Recommendations</h2>
      {data.map((rec, index) => (
        <div key={index} className="bg-white rounded-lg shadow-md p-6 border-l-4 border-indigo-500" data-testid={`recommendation-${index}`}>
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-900">{rec.category}</h3>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${priorityColors[rec.priority] || 'bg-gray-100 text-gray-800'}`}>
              {rec.priority} Priority
            </span>
          </div>
          <div className="space-y-2">
            <div>
              <p className="text-sm font-medium text-gray-700">Issue:</p>
              <p className="text-sm text-gray-600">{rec.issue}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Recommendation:</p>
              <p className="text-sm text-gray-600">{rec.recommendation}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default App;
