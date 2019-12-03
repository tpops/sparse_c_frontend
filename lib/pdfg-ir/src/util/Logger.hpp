#ifndef LOGGER_HPP
#define LOGGER_HPP

#include <cstdio>
#include <ctime>
#include <string>

using namespace std;

class Logger {
public:
	explicit Logger(const string& file = "") {
        _file = file;
		_status = !_file.empty();
	}

	virtual ~Logger() {}

	string file() const {
        return _file;
    }

	void file(const string& file) {
        _file = file;
    }

	void enable() {
        _status = true;
    }

    void disable() {
        _status = false;
    }

   void clear() {
       if (!_file.empty()) {
           remove(_file.c_str());
       }
   }

	void trace(const string& msg) {
        write("TRACE", msg);
    }

	void debug(const string& msg) {
        write("DEBUG", msg);
    }

	void info(const string& msg) {
        write("INFO", msg);
    }

	void warn(const string& msg) {
        write("WARN", msg);
    }

	void error(const string& msg) {
        write("ERROR", msg);
    }

	void fatal(const string& msg) {
        write("FATAL", msg);
    }

private:
    void write(const string& level, const string& msg) {
        char timestamp[1024];
        int isOpen = 0;
        FILE *file;

        time_t cal;
        struct tm *ltime;

        if (_status) {
            // 2014-08-25 16:19:37 [INFO ]: Updating file ...
            cal = (time_t) time(0);
            ltime = localtime(&cal);
            sprintf(timestamp, "%04d-%02d-%02d %02d:%02d:%02d", ltime->tm_year + 1900,
                    ltime->tm_mon + 1, ltime->tm_mday, ltime->tm_hour, ltime->tm_min, ltime->tm_sec);

            if (!_file.empty()) {
                file = fopen(_file.c_str(), "a");
                isOpen = (file != nullptr);
            }

            if (!isOpen) {
                file = stdout;
            }

            fprintf(file, "%s [%s] %s\n", timestamp, level.c_str(), msg.c_str());

            if (isOpen) {
                fclose(file);
            }
        }
    }

	bool _status;
	string _file;
};

#endif /* LOGGER_HPP */
