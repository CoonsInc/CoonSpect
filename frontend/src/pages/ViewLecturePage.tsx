import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/organisms/Header";
import Footer from "../components/organisms/Footer";
import HowItWorksSection from "../components/organisms/HowItWorksSection";
import ExamplesSection from "../components/organisms/ExamplesSection";
import ViewLectureSection from "../components/organisms/ViewLectureSection";

const ViewLecturePage: React.FC = () => {
    const navigate = useNavigate();
    const mockData = {
    title: "Название чужой лекции",
    text: "### **Пример конспекта**",
    audioUrl: "" 
    };

    return (
        <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen flex flex-col font-sans overflow-x-hidden">
            <Header />
        
            <main className="flex-grow">
                <ViewLectureSection 
                title={mockData.title}
                text={mockData.text}
                audioUrl={mockData.audioUrl}
                onBack={() => navigate(-1)}
                />
            </main>

            <HowItWorksSection />
            <ExamplesSection />
            <Footer />
        </div>
    );
};

export default ViewLecturePage;
