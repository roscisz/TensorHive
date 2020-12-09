import moment from 'moment'

const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export function convertToLocal (schedule) {
  schedule.hourStartLocal = moment.utc(schedule.hourStart, 'HH:mm').local().format('HH:mm')
  schedule.hourEndLocal = moment.utc(schedule.hourEnd, 'HH:mm').local().format('HH:mm')
  schedule.scheduleDaysLocal = []
  if (compareHours(schedule.hourStart, schedule.hourEnd) === 1) { // day is arbitrary
    for (const day of schedule.scheduleDays) {
      let newDay = weekdays.indexOf(day)
      if (isToTheRightOfUTC()) {
        newDay += 1
      } else {
        newDay -= 1
      }
      if (newDay < 0) newDay += 7
      newDay %= 7
      schedule.scheduleDaysLocal.push(weekdays[newDay])
    }
    schedule.scheduleDaysLocal = sortDayArray(schedule.scheduleDaysLocal)
  } else {
    schedule.scheduleDaysLocal = schedule.scheduleDays
  }
}

export function convertToUTC (schedule) {
  schedule.hourStart = moment(schedule.hourStartLocal, 'HH:mm').add(new Date().getTimezoneOffset(), 'minutes').format('HH:mm')
  schedule.hourEnd = moment(schedule.hourEndLocal, 'HH:mm').add(new Date().getTimezoneOffset(), 'minutes').format('HH:mm')
  schedule.scheduleDays = []
  if (compareHours(schedule.hourStart, schedule.hourEnd) === 1) { // day is arbitrary
    for (const day of schedule.scheduleDaysLocal) {
      let newDay = weekdays.indexOf(day)
      if (isToTheRightOfUTC()) {
        newDay -= 1
      } else {
        newDay += 1
      }
      if (newDay < 0) newDay += 7
      newDay %= 7
      schedule.scheduleDays.push(weekdays[newDay])
    }
    schedule.scheduleDays = sortDayArray(schedule.scheduleDays)
  } else {
    schedule.scheduleDays = schedule.scheduleDaysLocal
  }
}

function isToTheRightOfUTC () {
  return new Date().getTimezoneOffset() < 0
}

function compareHours (hourA, hourB) {
  const dateA = Date.parse('01/01/2011 ' + hourA)
  const dateB = Date.parse('01/01/2011 ' + hourB) // date is chosen arbitrarily
  return Math.sign(dateA - dateB)
}

function sortDayArray (days) {
  const correctOrder = weekdays
  return days.sort(function (a, b) {
    return correctOrder.indexOf(a) - correctOrder.indexOf(b)
  })
}
