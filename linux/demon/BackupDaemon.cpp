#include <windows.h>
#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <thread>
#include <boost/filesystem.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/log/trivial.hpp>

namespace fs = boost::filesystem;
namespace pt = boost::property_tree;

class BackupDaemon {
public:
    BackupDaemon(const std::string& configFile) {
        loadConfig(configFile);
        setupLogging();
    }

    void run() {
        while (running) {
            backupFiles();
            std::this_thread::sleep_for(std::chrono::seconds(backupInterval));
        }
    }

    void stop() {
        running = false;
    }

private:
    void loadConfig(const std::string& configFile) {
        pt::ptree root;
        pt::read_json(configFile, root);
        sourceDirectory = root.get<std::string>("source_directory");
        backupDirectory = root.get<std::string>("backup_directory");
        backupInterval = root.get<int>("backup_interval");
        logFile = root.get<std::string>("log_file");
    }

    void setupLogging() {
        boost::log::core::get()->set_filter(boost::log::trivial::severity >= boost::log::trivial::info);
        boost::log::add_file_log(boost::log::keywords::file_name = logFile,
                                 boost::log::keywords::rotation_size = 1048576,
                                 boost::log::keywords::max_size = 5242880);
    }

    void backupFiles() {
        auto timestamp = std::time(nullptr);
        std::string backupPath = backupDirectory + "\\backup_" + std::to_string(timestamp);
        try {
            fs::copy(sourceDirectory, backupPath);
            BOOST_LOG_TRIVIAL(info) << "Backup created at " << backupPath;
        } catch (const fs::filesystem_error& e) {
            BOOST_LOG_TRIVIAL(error) << "Backup failed: " << e.what();
        }
    }

    std::string sourceDirectory;
    std::string backupDirectory;
    int backupInterval;
    std::string logFile;
    bool running = true;
};

SERVICE_STATUS ServiceStatus;
SERVICE_STATUS_HANDLE hStatus;
BackupDaemon* daemon = nullptr;

void WINAPI ServiceMain(DWORD argc, LPTSTR* argv);
void WINAPI ServiceCtrlHandler(DWORD request);

void WINAPI ServiceMain(DWORD argc, LPTSTR* argv) {
    ServiceStatus.dwServiceType = SERVICE_WIN32;
    ServiceStatus.dwCurrentState = SERVICE_START_PENDING;
    ServiceStatus.dwControlsAccepted = SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN;
    ServiceStatus.dwWin32ExitCode = 0;
    ServiceStatus.dwServiceSpecificExitCode = 0;
    ServiceStatus.dwCheckPoint = 0;
    ServiceStatus.dwWaitHint = 0;

    hStatus = RegisterServiceCtrlHandler("BackupDaemon", ServiceCtrlHandler);
    if (hStatus == NULL) {
        return;
    }

    ServiceStatus.dwCurrentState = SERVICE_RUNNING;
    SetServiceStatus(hStatus, &ServiceStatus);

    daemon = new BackupDaemon("C:\\IT\\Jasur-Labs\\linux\\demon\\config.json");
    daemon->run();
}

void WINAPI ServiceCtrlHandler(DWORD request) {
    switch (request) {
    case SERVICE_CONTROL_STOP:
        ServiceStatus.dwCurrentState = SERVICE_STOP_PENDING;
        SetServiceStatus(hStatus, &ServiceStatus);
        daemon->stop();
        ServiceStatus.dwCurrentState = SERVICE_STOPPED;
        SetServiceStatus(hStatus, &ServiceStatus);
        break;
    case SERVICE_CONTROL_SHUTDOWN:
        ServiceStatus.dwCurrentState = SERVICE_STOP_PENDING;
        SetServiceStatus(hStatus, &ServiceStatus);
        daemon->stop();
        ServiceStatus.dwCurrentState = SERVICE_STOPPED;
        SetServiceStatus(hStatus, &ServiceStatus);
        break;
    default:
        break;
    }
}

int main(int argc, char* argv[]) {
    SERVICE_TABLE_ENTRY ServiceTable[] = {
        { "BackupDaemon", (LPSERVICE_MAIN_FUNCTION)ServiceMain },
        { NULL, NULL }
    };

    if (StartServiceCtrlDispatcher(ServiceTable) == FALSE) {
        return GetLastError();
    }

    return 0;
}