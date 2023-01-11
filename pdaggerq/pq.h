//
// pdaggerq - A code for bringing strings of creation / annihilation operators to normal order.
// Filename: pq.h
// Copyright (C) 2020 A. Eugene DePrince III
//
// Author: A. Eugene DePrince III <adeprince@fsu.edu>
// Maintainer: DePrince group
//
// This file is part of the pdaggerq package.
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.
//

#ifndef SQE_H
#define SQE_H

#include "data.h"

namespace pdaggerq {

class pq {

  private:

  public:

    /// constructor
    pq(std::string vacuum_type);

    /// destructor
    ~pq();

    /// detailed information about string (amplitudes, bosons, integrals, deltas, etc.)
    std::shared_ptr<StringData> data;

    /// expand sums to include spin and zero terms where appropriate
    void spin_blocking(std::vector<std::shared_ptr<pq> > &spin_blocked, std::map<std::string, std::string> spin_map);

    /// set non-summed spin labels
    void set_non_summed_spin_labels(std::vector<std::string> occ_spin_labels, std::vector<std::string> vir_spin_labels);

    /// add spin labels to a string
    bool add_spins(std::vector<std::shared_ptr<pq> > &list);

};

}

#endif
