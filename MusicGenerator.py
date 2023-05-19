import random
from midiutil import MIDIFile
from Intervalle import *
from MusicPlayer import play_music
from opensimplex import OpenSimplex

random.seed(random.randint(0, 1000000000000000000000))

dur_kadenz = [
    {
        "pitch": 0,
        "dur": True,
        "sept": False,
        "role": "T"
    },  # T
    {
        "pitch": (-kTerz),
        "dur": False,
        "sept": False,
        "role": "TP"
    },  # TP
    {
        "pitch": (-Quinte),
        "dur": True,
        "sept": False,
        "role": "S"
    },  # S
    {
        "pitch": (-Quinte - kTerz),
        "dur": False,
        "sept": False,
        "role": "SP"
    },  # SP
    {
        "pitch": Quinte,
        "dur": True,
        "sept": False,
        "role": "D"
    },  # D
    {
        "pitch": Quinte,
        "dur": True,
        "sept": True,
        "role": "D7"
    },  # D7
]


class Noise:
    def __init__(self):
        self.seed = random.randint(0, 1000000000000000)
        self.scale = 20#random.random() * 10# + 50
        self.open_simplex = OpenSimplex(self.seed)

    def get(self, x):
        return self.open_simplex.noise2(x=x * self.scale, y=0)


class Song:
    def __init__(self, tempo=random.randint(80, 170), beat=random.choice([2, 3, 4]), key=random.randint(54, 62)):
        self.tempo = tempo
        self.beat = beat
        self.key = key

        self.melody_channel = 1
        self.baseline_channel = 2
        self.chords_channel = 3

        self.midi = MIDIFile()
        self.midi.addTrackName(track=0, time=0, trackName="Track1")
        self.midi.addTempo(track=0, time=0, tempo=self.tempo)
        self.midi.addTimeSignature(track=0, time=0, numerator=beat, denominator=2, clocks_per_tick=24)
        self.noise = Noise()

        print(f"Tempo: {self.tempo} BPM")
        print(f"Taktart: {self.beat}/4")
        print(f"Tonhöhe: {self.key}")

        self.patterns = []

    def generate_pattern(self, duration=4):
        durations = {}
        time_left = duration
        for i in list(range(duration, 0, -1)):
            count = random.randrange(0, int(time_left / i), 1)
            durations[i] = count
            time_left -= count * i
        durations[0.5] = int(time_left / 0.5)
        
        # quarter_notes = int(duration * random.random())
        # half_notes = (duration - quarter_notes) * 2
        pattern = []
        noise_position = random.randint(0, 100000000)
        for n in range(sum([item[1] for item in list(durations.items())])):
            t = n + noise_position
            intervall = int(self.noise.get(t) * Quinte)
            # if half_notes == 0:
            #     length = 1
            # elif quarter_notes == 0:
            #     length = 0.5
            # else:
            #     length = random.choice([0.5, 1])
            # if length == 1:
            #     quarter_notes -= 1
            # else:
            #     half_notes -= 1
            length = 0
            while length == 0:
                l = random.choice(list(durations.keys()))
                if durations[l] > 0:
                    length = l
                    durations[l] -= 1
                else:
                    durations.pop(l)
            
            pattern.append((intervall, length))
        return pattern, duration

    @staticmethod
    def get_tl(pitch=60, dur=True):
        dur_tl = [0,
                  #gSekunde,
                  gTerz,
                  Quinte,
                  #gSexte,
                  Oktave]
        moll_tl = [0,
                   #gSekunde,
                   kTerz,
                   Quinte,
                   #kSexte,
                   Oktave]
        tl = [pitch + i for i in (dur_tl if dur else moll_tl)]
        tl += [i + Oktave for i in tl]
        tl += [i - Oktave for i in tl]
        tl = list(set(tl))
        return sorted(tl)

    def generate_patterns(self, number=random.randrange(2, 7)):
        random.shuffle(dur_kadenz)
        for _ in range(number):
            self.patterns.append(self.generate_pattern(self.beat))
        print(f"Anzahl Patterns: {len(self.patterns)}")

    def play_chord(self, pitch=60, duration=1, time=0, volume=100, track=0,
                   dur=True, sept=False, arpeggio=False, arpeggio_speed=8):
        dur_dreiklang = [0, gTerz, Quinte]
        moll_dreiklang = [0, kTerz, Quinte]
        chord = dur_dreiklang if dur else moll_dreiklang
        if sept:
            chord.append(kSeptime)

        for i, p in enumerate(chord):
            p = pitch + p
            chord[i] = min([p, p-Oktave, p-Oktave*2, p+Oktave, p+Oktave*2], key=lambda x: abs(x-self.key))

        for i, p in enumerate(chord):
            t = time + i / arpeggio_speed if arpeggio else time

            self.midi.addNote(track=track, channel=self.chords_channel, pitch=p, time=t, duration=duration,
                              volume=int(volume * (random.random() * 0.3 + 0.7)))

    def play_pattern(self, pattern, allowed_pitches, pitch=60, time=0, volume=100, track=0, baseline=False):
        for intervall, length in pattern:
            note = pitch + intervall
            note = min(allowed_pitches, key=lambda x: abs(note - x))

            self.midi.addNote(track=track, channel=self.melody_channel, pitch=note, time=time, duration=length,
                              volume=int(volume * (random.random() * 0.3 + 0.7)))
            if baseline and time == int(time):
                self.midi.addNote(track=track, channel=self.baseline_channel, pitch=note - Oktave, time=time + 1 / 16,
                                  duration=1, volume=int(volume * 0.65 * (random.random() * 0.3 + 0.7)))
            time += length
        return time

    def generate_song(self, length=5):
        time = 0
        for i in range(length):
            for k in dur_kadenz:
                played = False
                while not played or random.random() < 0.5:
                    self.play_chord(pitch=self.key + k["pitch"], time=time, duration=self.beat,
                                    dur=k["dur"], sept=k["sept"], volume=90, arpeggio=False, arpeggio_speed=32)
                    tl = self.get_tl(pitch=self.key, dur=k["dur"])
                    pattern = random.choice(self.patterns)
                    self.play_pattern(pattern[0], tl, self.key + k["pitch"] + Oktave,
                                      time=time, volume=100, baseline=True)
                    time += pattern[1]
                    played = True
                    if k["sept"] or "P" in k["role"]:
                        break
            # random.shuffle(dur_kadenz)

        self.play_chord(pitch=self.key, time=time, duration=8)

        print(f"Anzahl Wiederholungen: {i + 1}")
        print(f"Anzahl Takte: {(time - 1) // self.beat + 1}")

    def write_midi(self, path="output.mid"):
        with open(path, "wb") as f:
            self.midi.writeFile(f)


if __name__ == "__main__": 
    song = Song()
    song.generate_patterns(5)
    song.generate_song()
    song.write_midi("output/output.mid")
    # play_music("output.mid")
