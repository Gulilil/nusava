"use client";
import React, { useState, useEffect } from 'react';
import { Navbar } from '@/components/navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    Bot,
    Play,
    Square,
    RefreshCw,
    Settings
} from 'lucide-react';

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

interface AutomationStatus {
    is_running: boolean;
    user_id: number;
    thread_name?: string;
}

export default function AutomationDashboard() {
    const [automationStatus, setAutomationStatus] = useState<AutomationStatus>();
    const [loading, setLoading] = useState(true);
    const [stopping, setStopping] = useState(false);
    const [starting, setStarting] = useState(false);

    // New states for interval inputs
    const [minInterval, setMinInterval] = useState(5); // in minutes
    const [maxInterval, setMaxInterval] = useState(15); // in minutes
    const [token, setToken] = useState<string | null>(null);

    useEffect(() => {
        // Access localStorage inside useEffect to avoid SSR issues
        const accessToken = localStorage.getItem('access_token') || localStorage.getItem('jwtToken');
        setToken(accessToken);
    }, []);

    useEffect(() => {
        // Only check status when token is available
        if (token) {
            checkAutomationStatus();
        }
    }, [token]);

    const checkAutomationStatus = async () => {
        if (!token) return;

        setLoading(true);
        try {
            const response = await fetch(`${API}/automation/status/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            setAutomationStatus(data.data);
        } catch (error) {
            console.error('Error checking automation status:', error);
        } finally {
            setLoading(false);
        }
    };

    const stopAutomation = async () => {
        if (!token) return;

        setStopping(true);
        try {
            const response = await fetch(`${API}/automation/stop/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                await checkAutomationStatus();
            } else {
                console.error(data.message);
            }
        } catch (error) {
            console.error('Error stopping automation:', error);
        } finally {
            setStopping(false);
        }
    };

    const startAutomation = async () => {
        if (!token) return;

        // Validation
        if (minInterval <= 0 || maxInterval <= 0) {
            alert('Intervals must be greater than 0');
            return;
        }
        if (minInterval >= maxInterval) {
            alert('Minimum interval must be less than maximum interval');
            return;
        }
        if (minInterval < 3) {
            alert('Minimum interval should be at least 3 minutes to avoid rate limits');
            return;
        }

        setStarting(true);
        try {
            const response = await fetch(`${API}/automation/start/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    min_interval: minInterval * 60, // Convert to seconds
                    max_interval: maxInterval * 60  // Convert to seconds
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                await checkAutomationStatus();
            } else {
                console.error(data.message);
                alert(`Error: ${data.message}`);
            }
        } catch (error) {
            console.error('Error starting automation:', error);
            alert('Error starting automation');
        } finally {
            setStarting(false);
        }
    };

    // Show loading state while token is being retrieved
    if (!token) {
        return (
            <div className="flex flex-col min-h-screen">
                <Navbar title="DM Automation" />
                <main className="flex-1 p-6 space-y-6">
                    <div className="flex items-center justify-center h-32">
                        <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                        <span>Loading...</span>
                    </div>
                </main>
            </div>
        );
    }

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar title="DM Automation" />
            <main className="flex-1 p-6 space-y-6">

                {/* Single Status Card */}
                <Card className="max-w-2xl mx-auto">
                    <CardHeader>
                        <CardTitle className="flex items-center">
                            <Bot className="mr-2 h-5 w-5" />
                            DM Automation Status
                        </CardTitle>
                        <CardDescription>
                            Control your Instagram DM automation system
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">

                        {/* Status Display */}
                        <div className="text-center">
                            {loading ? (
                                <div className="flex items-center justify-center">
                                    <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                                    <span>Checking status...</span>
                                </div>
                            ) : (
                                <div className="space-y-2">
                                    <div className="text-3xl font-bold">
                                        {automationStatus?.is_running ? (
                                            <span className="text-green-600">🟢 Running</span>
                                        ) : (
                                            <span className="text-red-600">🔴 Stopped</span>
                                        )}
                                    </div>
                                    <p className="text-muted-foreground">
                                        {automationStatus?.is_running
                                            ? 'Your DM automation is actively responding to messages'
                                            : 'DM automation is currently inactive'
                                        }
                                    </p>
                                    {automationStatus?.thread_name && (
                                        <p className="text-sm text-muted-foreground">
                                            Thread: {automationStatus.thread_name}
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Interval Settings */}
                        {!automationStatus?.is_running && (
                            <div className="border rounded-lg p-4 space-y-4">
                                <h4 className="font-medium flex items-center">
                                    <Settings className="h-4 w-4 mr-2" />
                                    Automation Timing Settings
                                </h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="minInterval">Minimum Interval (minutes)</Label>
                                        <Input
                                            id="minInterval"
                                            type="number"
                                            min="3"
                                            max="60"
                                            value={minInterval}
                                            onChange={(e) => setMinInterval(Number(e.target.value))}
                                            placeholder="5"
                                        />
                                        <p className="text-xs text-muted-foreground">
                                            Fastest check frequency (minimum 1 minutes)
                                        </p>
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="maxInterval">Maximum Interval (minutes)</Label>
                                        <Input
                                            id="maxInterval"
                                            type="number"
                                            min="5"
                                            max="120"
                                            value={maxInterval}
                                            onChange={(e) => setMaxInterval(Number(e.target.value))}
                                            placeholder="15"
                                        />
                                        <p className="text-xs text-muted-foreground">
                                            Slowest check frequency (up to 2 hours)
                                        </p>
                                    </div>
                                </div>
                                <div className="bg-blue-50 dark:bg-blue-950 p-3 rounded-md">
                                    <p className="text-sm text-blue-700 dark:text-blue-300">
                                        💡 <strong>Tip:</strong> Random intervals between 3-5 minutes help avoid Instagram rate limits
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* Control Buttons */}
                        <div className="flex justify-center gap-3">
                            {automationStatus?.is_running ? (
                                <Button
                                    onClick={stopAutomation}
                                    disabled={stopping || loading}
                                    variant="destructive"
                                    className="min-w-[120px]"
                                >
                                    {stopping ? (
                                        <>
                                            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                                            Stopping...
                                        </>
                                    ) : (
                                        <>
                                            <Square className="h-4 w-4 mr-2" />
                                            Stop
                                        </>
                                    )}
                                </Button>
                            ) : (
                                <Button
                                    onClick={startAutomation}
                                    disabled={starting || loading || minInterval >= maxInterval || minInterval < 1}
                                    className="min-w-[120px]"
                                >
                                    {starting ? (
                                        <>
                                            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                                            Starting...
                                        </>
                                    ) : (
                                        <>
                                            <Play className="h-4 w-4 mr-2" />
                                            Start Automation
                                        </>
                                    )}
                                </Button>
                            )}

                            <Button
                                onClick={checkAutomationStatus}
                                variant="outline"
                                disabled={loading}
                                className="min-w-[120px]"
                            >
                                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                                Refresh
                            </Button>
                        </div>

                    </CardContent>
                </Card>

            </main>
        </div>
    );
}