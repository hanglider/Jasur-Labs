#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <thread>
#include <boost/filesystem.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/log/trivial.hpp>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <signal.h>

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
        std::string backupPath = backupDirectory + "/backup_" + std::to_string(timestamp);
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

BackupDaemon* daemon = nullptr;

void signalHandler(int signum) {
    if (daemon) {
        daemon->stop();
    }
}

int main(int argc, char* argv[]) {
    pid_t pid, sid;

    pid = fork();
    if (pid < 0) {
        std::cerr << "Fork failed!" << std::endl;
        exit(EXIT_FAILURE);
    }

    if (pid > 0) {
        exit(EXIT_SUCCESS);
    }

    umask(0);

    sid = setsid();
    if (sid < 0) {
        std::cerr << "Setsid failed!" << std::endl;
        exit(EXIT_FAILURE);
    }

    if ((chdir("/")) < 0) {
        std::cerr << "Chdir failed!" << std::endl;
        exit(EXIT_FAILURE);
    }

    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);

    signal(SIGTERM, signalHandler);
    signal(SIGINT, signalHandler);

    daemon = new BackupDaemon("/path/to/config.json");
    daemon->run();

    delete daemon;
    return 0;
}
