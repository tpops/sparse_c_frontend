#ifndef _PROFILER_HPP_
#define _PROFILER_HPP_

#include <sys/time.h>

#define MICRO 1e-6
#ifndef NULL
#define NULL 0
#endif

using namespace std;

class Profiler
{
    public:
		static Profiler& instance() {
			static Profiler instance;

			return instance;
		}

		Profiler() {}

        virtual ~Profiler() {}

        void start() {
			gettimeofday(&_startTime, NULL);
		}

        void stop() {
			gettimeofday(&_stopTime, NULL);
		}

        void reset() {
			stop();
			start();
		}

        double startTime() {
            return (double) _startTime.tv_sec + (((double) _startTime.tv_usec) * MICRO);
		}

        double stopTime() {
            return (double) _stopTime.tv_sec + (((double) _stopTime.tv_usec) * MICRO);
		}

        double elapsed() {
			return (stopTime() - startTime());
		}

    private:
        struct timeval _startTime;
        struct timeval _stopTime;
};

#endif // _PROFILER_HPP_
