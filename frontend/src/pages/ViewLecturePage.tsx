import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTextStore } from "../stores";
import Header from "../components/organisms/Header";
import Footer from "../components/organisms/Footer";
import HowItWorksSection from "../components/organisms/HowItWorksSection";
import ExamplesSection from "../components/organisms/ExamplesSection";
import ViewLectureSection from "../components/organisms/ViewLectureSection";

const ViewLecturePage: React.FC = () => {
    const navigate = useNavigate();
    const { currentLecture, audioUrl, restoreAudio } = useTextStore();

    useEffect(() => {
        restoreAudio();
    }, [restoreAudio]);

    if (!currentLecture) return null;

    return (
        <div className="bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] min-h-screen flex flex-col font-sans overflow-x-hidden">
            <Header />
        
            <main className="flex-grow">
                <ViewLectureSection 
                    title={currentLecture.name}
                    text={currentLecture.text}
                    audioUrl={audioUrl ?? undefined} 
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
